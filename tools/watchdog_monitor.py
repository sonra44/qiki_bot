

# -*- coding: utf-8 -*-
"""
QIKI Bot
Watchdog Monitor - Monitors the health and freshness of key system files.
"""
import os
import json
import time
import argparse
import datetime
import logging
from typing import Dict, List

# --- Path Setup ---
# Ensure the script can find the core modules
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from core.file_paths import FSM_STATE_FILE, TELEMETRY_FILE, MISSION_STATUS_FILE

# --- Constants ---
LOG_DIR = os.path.join(os.path.dirname(__file__), '..', 'logs')
WATCHDOG_LOG_FILE = os.path.join(LOG_DIR, 'watchdog_status.json')
TASK_STATE_FILE = os.path.join(os.path.dirname(__file__), '..', 'task_state.json')

# --- Monitored Files Configuration ---
FILES_TO_MONITOR = {
    "fsm_state.json": FSM_STATE_FILE,
    "telemetry.json": TELEMETRY_FILE,
    "mission_status.json": MISSION_STATUS_FILE,
    "task_state.json": TASK_STATE_FILE,
}

class WatchdogMonitor:
    """
    Checks key system files for existence, freshness (staleness), and basic integrity.
    """
    def __init__(self, log_to_file: bool = False, verbose: bool = False, exit_on_fail: bool = False):
        self.log_to_file = log_to_file
        self.verbose = verbose
        self.exit_on_fail = exit_on_fail
        self.statuses: Dict[str, str] = {}
        self.last_sizes: Dict[str, int] = {}

        if not os.path.exists(LOG_DIR):
            os.makedirs(LOG_DIR)

    def check_file(self, file_key: str, file_path: str, max_age_sec: int = 3) -> str:
        """
        Performs all checks on a single file.
        Returns the status: "OK", "STALE", "MISSING", or "CORRUPTED".
        """
        if not os.path.exists(file_path):
            return "MISSING"

        try:
            file_size = os.path.getsize(file_path)
            if file_size == 0:
                return "CORRUPTED"

            # Check for drastic size changes if we have a history
            if file_key in self.last_sizes and self.last_sizes[file_key] > 0:
                # Simple corruption check: if the file becomes empty after having content
                if file_size == 0:
                     return "CORRUPTED"
            self.last_sizes[file_key] = file_size

            last_modified_time = os.path.getmtime(file_path)
            age = time.time() - last_modified_time
            if age > max_age_sec:
                if self.verbose:
                    print(f"\033[93m[WDG] {file_key: <20} : STALE (Last update: {age:.1f}s ago)\033[0m")
                return "STALE"

            return "OK"

        except OSError as e:
            if self.verbose:
                print(f"\033[91m[WDG] Error accessing {file_key}: {e}\033[0m")
            return "ERROR"


    def run(self):
        """
        Runs a single check cycle on all monitored files.
        """
        self.statuses = {"timestamp": datetime.datetime.now().isoformat()}
        has_critical_failure = False

        for key, path in FILES_TO_MONITOR.items():
            status = self.check_file(key, path)
            self.statuses[key] = status

            if self.verbose and status != "STALE": # Stale is already printed
                color = "\033[92m" if status == "OK" else "\033[91m"
                print(f"{color}[WDG] {key: <20} : {status}\033[0m")

            if status in ["MISSING", "CORRUPTED", "ERROR"]:
                has_critical_failure = True

        if self.log_to_file:
            with open(WATCHDOG_LOG_FILE, 'w') as f:
                json.dump(self.statuses, f, indent=4)

        if self.exit_on_fail and has_critical_failure:
            print("\033[91m[WDG] Critical failure detected. Exiting as per --exit-on-fail.\033[0m")
            sys.exit(1)

    def watch(self, interval: int = 1):
        """
        Runs the check continuously in a loop.
        """
        print("Starting watchdog monitor... Press Ctrl+C to stop.")
        while True:
            try:
                if self.verbose:
                    # Clear screen for a cleaner look in watch mode
                    print("\033[H\033[J", end="")
                    print(f"--- Watchdog Monitor @ {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ---")
                self.run()
                time.sleep(interval)
            except KeyboardInterrupt:
                print("\nStopping watchdog monitor.")
                break
            except Exception as e:
                print(f"\033[91mAn unexpected error occurred: {e}\033[0m")
                time.sleep(interval)


def main():
    parser = argparse.ArgumentParser(description="QIKI Bot Watchdog Monitor.")
    parser.add_argument("--watch", action="store_true", default=True, help="Run continuously (default).")
    parser.add_argument("--once", action="store_true", help="Run only once and exit.")
    parser.add_argument("--log", action="store_true", help="Enable writing status to logs/watchdog_status.json.")
    parser.add_argument("--verbose", "-v", action="store_true", help="Print status to standard output.")
    parser.add_argument("--exit-on-fail", action="store_true", help="Exit with status 1 if a file is MISSING or CORRUPTED.")
    parser.add_argument("--interval", type=int, default=1, help="Check interval in seconds for watch mode.")

    args = parser.parse_args()

    if args.once:
        args.watch = False # --once overrides --watch

    # Create a placeholder for the task state file if it doesn't exist
    if not os.path.exists(TASK_STATE_FILE):
        with open(TASK_STATE_FILE, 'w') as f:
            json.dump({"status": "uninitialized", "timestamp": datetime.datetime.now().isoformat()}, f)

    monitor = WatchdogMonitor(log_to_file=args.log, verbose=args.verbose, exit_on_fail=args.exit_on_fail)

    if args.watch:
        monitor.watch(interval=args.interval)
    else:
        monitor.run()

if __name__ == "__main__":
    main()
