# -*- coding: utf-8 -*-
"""
QIKI Bot
System Consistency Checker
"""
import json
import os
import time
import argparse
import logging
import datetime
from typing import Dict, Any, List

# --- Path Setup ---
# Ensure the script can find the core modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from core.file_paths import FSM_STATE_FILE, SENSORS_FILE, TELEMETRY_FILE, MISSION_STATUS_FILE
from core.fsm_client import FSMClient

# --- Log Setup ---
LOG_DIR = os.path.join(os.path.dirname(__file__), '..', 'logs')
CONSISTENCY_LOG_FILE = os.path.join(LOG_DIR, 'consistency_log.json')
CRASH_LOG_FILE = os.path.join(LOG_DIR, 'qiki_crash.log')

if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

# Logger for critical, crash-like errors
crash_logger = logging.getLogger('CrashLogger')
crash_handler = logging.FileHandler(CRASH_LOG_FILE)
crash_handler.setFormatter(logging.Formatter('%(asctime)s [%(levelname)s] %(message)s'))
crash_logger.addHandler(crash_handler)
crash_logger.setLevel(logging.ERROR)

class ConsistencyChecker:
    """
    Monitors the system's state files and checks for logical inconsistencies.
    """
    def __init__(self, verbose=False):
        self.verbose = verbose
        self.issues = []
        self.fsm_client = FSMClient()

    def log_issue(self, level: str, check_type: str, message: str, details: Dict[str, Any]):
        """Logs a consistency issue."""
        issue = {
            "timestamp": datetime.datetime.now().isoformat(),
            "level": level.upper(),
            "check_type": check_type,
            "message": message,
            "details": details
        }
        self.issues.append(issue)
        
        if self.verbose:
            print(f"[{issue['level']}] {issue['message']} | Details: {issue['details']}")

        if level.upper() == "ERROR":
            crash_logger.error(f"{message} | Details: {json.dumps(details)}")

    def load_json_safely(self, file_path: str) -> Dict[str, Any]:
        """Safely loads a JSON file, returning None on failure."""
        if not os.path.exists(file_path):
            self.log_issue("WARNING", "file_check", f"File not found: {os.path.basename(file_path)}", {"path": file_path})
            return None
        try:
            with open(file_path, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            self.log_issue("ERROR", "file_check", f"Failed to read or parse {os.path.basename(file_path)}", {"path": file_path, "error": str(e)})
            return None

    def check_staleness(self, data: Dict[str, Any], filename: str, max_age_sec: int = 5):
        """Checks if a file is too old based on its timestamp."""
        ts_str = data.get("timestamp") or data.get("last_update")
        if not ts_str:
            self.log_issue("WARNING", "staleness_check", f"Missing timestamp in {filename}", {"file": filename})
            return

        try:
            ts = datetime.datetime.fromisoformat(ts_str)
            age = (datetime.datetime.now() - ts).total_seconds()
            if age > max_age_sec:
                self.log_issue("WARNING", "staleness_check", f"{filename} is stale (updated {age:.1f}s ago)", {"file": filename, "age_sec": age})
        except (ValueError, TypeError):
            self.log_issue("WARNING", "staleness_check", f"Invalid timestamp format in {filename}", {"file": filename, "timestamp": ts_str})

    def run_checks(self):
        """Executes all consistency checks."""
        self.issues = []
        
        # 1. Load all state files
        fsm_state = self.fsm_client.get_state()
        sensors = self.load_json_safely(SENSORS_FILE)
        telemetry = self.load_json_safely(TELEMETRY_FILE)
        mission = self.load_json_safely(MISSION_STATUS_FILE)

        # 2. Run checks if data is available
        if fsm_state and sensors:
            self.check_fsm_vs_sensors(fsm_state, sensors)
        
        if fsm_state and mission:
            self.check_fsm_vs_mission(fsm_state, mission)

        if telemetry:
            self.check_staleness(telemetry, "telemetry.json")
        
        if fsm_state:
            self.check_staleness(fsm_state, "fsm_state.json")

        # 3. Write results to log file
        if self.issues:
            self.write_log_file()

    def check_fsm_vs_sensors(self, fsm: Dict[str, Any], sensors: Dict[str, Any]):
        """Checks for inconsistencies between FSM state and sensor readings."""
        fsm_s = fsm.get("current_state", "UNKNOWN")
        
        # Check charging status vs. battery level
        if fsm_s == "CHARGING" and sensors.get("Power", {}).get("battery", {}).get("soc", 0) >= 98:
            self.log_issue("WARNING", "fsm_vs_sensors", "FSM is CHARGING but battery is nearly full.", {"fsm_state": fsm_s, "battery_soc": sensors.get("Power", {}).get("battery", {}).get("soc")})

        # Check active status vs. navigation sensors
        if fsm_s == "MISSION_ACTIVE" and sensors.get("Navigation", {}).get("status") != "OK":
            self.log_issue("WARNING", "fsm_vs_sensors", "FSM is ACTIVE but navigation status is not OK.", {"fsm_state": fsm_s, "nav_status": sensors.get("Navigation", {}).get("status")})

        # Check idle status vs. thrusters
        if fsm_s == "IDLE" and sensors.get("Thrusters", {}).get("active") is True:
            self.log_issue("ERROR", "fsm_vs_sensors", "FSM is IDLE but thrusters are reported as active.", {"fsm_state": fsm_s, "thrusters_active": True})

    def check_fsm_vs_mission(self, fsm: Dict[str, Any], mission: Dict[str, Any]):
        """Checks for inconsistencies between FSM state and mission status."""
        fsm_s = fsm.get("current_state", "UNKNOWN")
        mission_s = mission.get("status", "UNKNOWN")

        if fsm_s == "MISSION_ACTIVE" and not os.path.exists(MISSION_STATUS_FILE):
             self.log_issue("ERROR", "fsm_vs_mission", "FSM is in MISSION_ACTIVE state but mission file is missing.", {"fsm_state": fsm_s})

        if fsm_s == "IDLE" and mission_s == "active":
            self.log_issue("WARNING", "fsm_vs_mission", "FSM is IDLE but mission status is 'active'.", {"fsm_state": fsm_s, "mission_status": mission_s})

    def write_log_file(self):
        """Writes the collected issues to the consistency log."""
        log_data = []
        if os.path.exists(CONSISTENCY_LOG_FILE):
            try:
                with open(CONSISTENCY_LOG_FILE, 'r') as f:
                    log_data = json.load(f)
            except (json.JSONDecodeError, IOError):
                pass # Overwrite if corrupted
        
        log_data.extend(self.issues)
        
        with open(CONSISTENCY_LOG_FILE, 'w') as f:
            json.dump(log_data, f, indent=4)

    def run_once(self):
        """Run the checks a single time."""
        print("Running consistency check...")
        self.run_checks()
        if self.issues:
            print(f"Found {len(self.issues)} consistency issues. Check logs/consistency_log.json")
        else:
            print("No consistency issues found.")
        
        if any(issue['level'] == 'ERROR' for issue in self.issues):
            return "INCONSISTENT"
        return "CONSISTENT"

    def run_watch(self, interval: int = 5):
        """Run checks continuously in a loop."""
        print(f"Starting continuous consistency check (interval: {interval}s). Press Ctrl+C to stop.")
        while True:
            try:
                self.run_checks()
                time.sleep(interval)
            except KeyboardInterrupt:
                print("\nStopping watcher.")
                break

def main():
    """Main function to parse arguments and run the checker."""
    parser = argparse.ArgumentParser(description="QIKI Bot System Consistency Checker.")
    parser.add_argument("--once", action="store_true", help="Run the checks only once and exit.")
    parser.add_argument("--watch", action="store_true", default=True, help="Run checks continuously (default).")
    parser.add_argument("--interval", type=int, default=5, help="Interval in seconds for watch mode.")
    parser.add_argument("--verbose", "-v", action="store_true", help="Print issues to standard output as they are found.")
    
    args = parser.parse_args()

    # --once overrides --watch
    if args.once:
        args.watch = False

    checker = ConsistencyChecker(verbose=args.verbose)

    if args.watch:
        checker.run_watch(interval=args.interval)
    else:
        checker.run_once()

if __name__ == "__main__":
    main()