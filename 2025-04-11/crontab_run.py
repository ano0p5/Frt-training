
import subprocess
import sys
import os
from datetime import datetime

def log(message):
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {message}")

def main():
    script_path = "/home/anoop/frt/2025-04-11/crontab_test.py"

    if not os.path.exists(script_path):
        log(f"Script not found: {script_path}")
        sys.exit(1)

    log(f"Running {script_path}...")
    result = subprocess.run(["python3", script_path])

    if result.returncode == 0:
        log("Script ran successfully.")
    else:
        log("Script encountered an error.")

if __name__ == "__main__":
    main()
