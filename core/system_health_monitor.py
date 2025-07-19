import os
import json
import time
from datetime import datetime

from core.file_paths import (
    FSM_STATE_FILE,
    TELEMETRY_FILE,
    MISSION_STATUS_FILE,
    SHARED_BUS_FILE,
    QIKI_BOOT_LOG_FILE,
    HEALTH_REPORT_LOG_FILE,
)

OK_THRESHOLD_SEC = 3
STALE_THRESHOLD_SEC = 10

os.makedirs(os.path.dirname(HEALTH_REPORT_LOG_FILE), exist_ok=True)


def read_json_file(filepath: str) -> dict:
    if not os.path.exists(filepath):
        return {"status": "MISSING"}
    try:
        with open(filepath, "r") as f:
            data = json.load(f)
            data["status"] = "OK"
            return data
    except json.JSONDecodeError:
        return {"status": "INVALID_JSON"}
    except Exception:
        return {"status": "ERROR_READING"}


def get_file_status(filepath: str) -> str:
    if not os.path.exists(filepath):
        return "MISSING"
    try:
        mod_time = datetime.fromtimestamp(os.path.getmtime(filepath))
        diff = datetime.now() - mod_time
        if diff.total_seconds() < OK_THRESHOLD_SEC:
            return "OK"
        if diff.total_seconds() < STALE_THRESHOLD_SEC:
            return "STALE"
        return "DEAD"
    except Exception:
        return "ERROR_CHECKING_TIME"


def monitor_system_health():
    health_report = {}
    files_to_monitor = {
        "fsm_state": FSM_STATE_FILE,
        "telemetry": TELEMETRY_FILE,
        "mission_state": MISSION_STATUS_FILE,
        "shared_bus": SHARED_BUS_FILE,
        "qiki_boot_log": QIKI_BOOT_LOG_FILE,
    }

    for key, path in files_to_monitor.items():
        health_report[key] = get_file_status(path)

    shared_bus_data = read_json_file(SHARED_BUS_FILE)
    agent_status = {}
    if isinstance(shared_bus_data.get("agents"), dict):
        for agent_id, info in shared_bus_data["agents"].items():
            hb = info.get("last_heartbeat")
            if hb:
                try:
                    if hb.endswith("Z"):
                        ts = datetime.fromisoformat(hb[:-1])
                    else:
                        ts = datetime.fromisoformat(hb)
                    diff = datetime.utcnow() - ts
                    if diff.total_seconds() < OK_THRESHOLD_SEC:
                        agent_status[agent_id] = "OK"
                    elif diff.total_seconds() < STALE_THRESHOLD_SEC:
                        agent_status[agent_id] = "STALE"
                    else:
                        agent_status[agent_id] = "DEAD"
                except ValueError:
                    agent_status[agent_id] = "INVALID_HEARTBEAT_FORMAT"
            else:
                agent_status[agent_id] = "NO_HEARTBEAT_DATA"
    health_report["agent_status"] = agent_status

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(HEALTH_REPORT_LOG_FILE, "a") as f:
        json.dump({timestamp: health_report}, f)
        f.write("\n")


if __name__ == "__main__":
    print("Starting System Health Monitor...")
    while True:
        monitor_system_health()
        time.sleep(5)
