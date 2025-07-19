import os
import json
import time
from datetime import datetime, timedelta

# --- File Paths ---
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
FSM_STATE_FILE = os.path.join(BASE_DIR, "fsm_state.json")
TELEMETRY_FILE = os.path.join(BASE_DIR, "telemetry.json")
MISSION_STATE_FILE = os.path.join(BASE_DIR, "mission_state.json")
SHARED_BUS_FILE = os.path.join(BASE_DIR, "shared_bus.json")
QIKI_BOOT_LOG_FILE = os.path.join(BASE_DIR, "qiki_boot_log.json")

LOG_DIR = os.path.join(BASE_DIR, "logs")
HEALTH_REPORT_LOG_FILE = os.path.join(LOG_DIR, "health_report.log")

os.makedirs(LOG_DIR, exist_ok=True)

# --- Thresholds ---
OK_THRESHOLD_SEC = 3
STALE_THRESHOLD_SEC = 10

# --- Helper Functions ---
def read_json_file(filepath: str) -> dict:
    """Safely reads a JSON file. Returns empty dict if file not found or invalid JSON."""
    if not os.path.exists(filepath):
        return {"status": "MISSING"}
    try:
        with open(filepath, 'r') as f:
            data = json.load(f)
            data["status"] = "OK" # Assume OK if successfully read
            return data
    except json.JSONDecodeError:
        return {"status": "INVALID_JSON"}
    except Exception:
        return {"status": "ERROR_READING"}

def get_file_status(filepath: str) -> str:
    """Checks file modification time and returns status (OK, STALE, DEAD, MISSING)."""
    if not os.path.exists(filepath):
        return "MISSING"
    
    try:
        mod_time = datetime.fromtimestamp(os.path.getmtime(filepath))
        time_diff = datetime.now() - mod_time

        if time_diff.total_seconds() < OK_THRESHOLD_SEC:
            return "OK"
        elif time_diff.total_seconds() < STALE_THRESHOLD_SEC:
            return "STALE"
        else:
            return "DEAD"
    except Exception:
        return "ERROR_CHECKING_TIME"

def monitor_system_health():
    health_report = {}

    # Monitor individual files
    files_to_monitor = {
        "fsm_state": FSM_STATE_FILE,
        "telemetry": TELEMETRY_FILE,
        "mission_state": MISSION_STATE_FILE,
        "shared_bus": SHARED_BUS_FILE,
        "qiki_boot_log": QIKI_BOOT_LOG_FILE
    }

    for key, filepath in files_to_monitor.items():
        health_report[key] = get_file_status(filepath)

    # Monitor agents in shared_bus.json
    shared_bus_data = read_json_file(SHARED_BUS_FILE)
    agent_status = {}
    if "agents" in shared_bus_data and isinstance(shared_bus_data["agents"], dict):
        for agent_id, agent_info in shared_bus_data["agents"].items():
            last_heartbeat_str = agent_info.get("last_heartbeat")
            if last_heartbeat_str:
                try:
                    # Handle both 'Z' and non-'Z' ISO formats
                    if last_heartbeat_str.endswith('Z'):
                        last_heartbeat_time = datetime.fromisoformat(last_heartbeat_str[:-1])
                    else:
                        last_heartbeat_time = datetime.fromisoformat(last_heartbeat_str)

                    time_diff = datetime.utcnow() - last_heartbeat_time

                    if time_diff.total_seconds() < OK_THRESHOLD_SEC:
                        agent_status[agent_id] = "OK"
                    elif time_diff.total_seconds() < STALE_THRESHOLD_SEC:
                        agent_status[agent_id] = "STALE"
                    else:
                        agent_status[agent_id] = "DEAD"
                except ValueError:
                    agent_status[agent_id] = "INVALID_HEARTBEAT_FORMAT"
            else:
                agent_status[agent_id] = "NO_HEARTBEAT_DATA"
    health_report["agent_status"] = agent_status

    # Log the report
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = {timestamp: health_report}

    with open(HEALTH_REPORT_LOG_FILE, 'a') as f:
        json.dump(log_entry, f)
        f.write('\n') # Add newline for readability

    print(f"Health report logged: {json.dumps(health_report, indent=2)}")

# --- Main Loop ---
if __name__ == "__main__":
    print("Starting System Health Monitor...")
    while True:
        monitor_system_health()
        time.sleep(5)
