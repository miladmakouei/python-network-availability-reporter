
import csv
import platform
import subprocess
from datetime import datetime
from pathlib import Path


TARGETS_FILE = Path("targets.txt")
REPORT_FILE = Path("network_report.csv")
PING_TIMEOUT = 5


def load_targets():
    if not TARGETS_FILE.exists():
        print("[-] targets.txt was not found.")
        return []

    targets = []

    with TARGETS_FILE.open("r", encoding="utf-8") as file:
        for line in file:
            target = line.strip()

            if target and not target.startswith("#"):
                targets.append(target)

    return list(dict.fromkeys(targets))


def check_target(target):
    system = platform.system().lower()

    if system == "windows":
        command = ["ping", "-n", "1", "-w", "4000", target]
    else:
        command = ["ping", "-c", "1", "-W", "4", target]

    start_time = datetime.now()

    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=PING_TIMEOUT
        )

        end_time = datetime.now()
        response_time = (
            end_time - start_time
        ).total_seconds() * 1000

        if result.returncode == 0:
            return {
                "target": target,
                "status": "ONLINE",
                "response_ms": round(response_time, 2)
            }

        return {
            "target": target,
            "status": "OFFLINE",
            "response_ms": ""
        }

    except subprocess.TimeoutExpired:
        return {
            "target": target,
            "status": "TIMEOUT",
            "response_ms": ""
        }

    except FileNotFoundError:
        return {
            "target": target,
            "status": "PING_NOT_FOUND",
            "response_ms": ""
        }


def save_report(results):
    fields = [
        "target",
        "status",
        "response_ms",
        "checked_at"
    ]

    try:
        with REPORT_FILE.open(
            "w",
            newline="",
            encoding="utf-8"
        ) as file:

            writer = csv.DictWriter(
                file,
                fieldnames=fields
            )

            writer.writeheader()

            checked_at = datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S"
            )

            for result in results:
                row = result.copy()
                row["checked_at"] = checked_at
                writer.writerow(row)

        print(f"\n[+] Report saved: {REPORT_FILE}")

    except OSError as error:
        print(f"\n[-] Could not save report: {error}")


def show_summary(results):
    online = sum(
        1 for result in results
        if result["status"] == "ONLINE"
    )

    offline = sum(
        1 for result in results
        if result["status"] == "OFFLINE"
    )

    other = len(results) - online - offline

    print("\n" + "=" * 50)
    print("              NETWORK REPORT")
    print("=" * 50)

    for result in results:
        response = result["response_ms"]

        if response != "":
            response = f"{response} ms"
        else:
            response = "-"

        print(
            f"{result['target']:<25} "
            f"{result['status']:<15} "
            f"{response}"
        )

    print("\n" + "-" * 50)
    print(f"Total Targets: {len(results)}")
    print(f"Online:        {online}")
    print(f"Offline:       {offline}")
    print(f"Other Results: {other}")
    print("=" * 50)


def main():
    print("=" * 50)
    print("       NETWORK AVAILABILITY REPORTER")
    print("=" * 50)

    targets = load_targets()

    if not targets:
        print("[-] No targets found in targets.txt.")
        return

    print(f"\n[*] Found {len(targets)} unique targets.")
    print("[*] Starting network checks...\n")

    results = []

    for target in targets:
        print(f"Checking {target} ...")

        result = check_target(target)
        results.append(result)

    show_summary(results)
    save_report(results)


if __name__ == "__main__":
    main()
