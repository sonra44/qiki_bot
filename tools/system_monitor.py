import os
import json
import time
from datetime import datetime
from pathlib import Path
import sys

# Add project root to sys.path for imports
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.append(project_root)

from core.fsm_client import FSMClient
from core.localization_manager import loc

# ANSI цвета (можно заменить colorama, если допустимо)
class Colors:
    RESET = "\u001b[0m"
    RED = "\u001b[91m"
    GREEN = "\u001b[92m"
    YELLOW = "\u001b[93m"
    CYAN = "\u001b[96m"
    MAGENTA = "\u001b[95m"
    GRAY = "\u001b[90m"
    BOLD = "\u001b[1m"

DATA_DIR = Path(__file__).parent.parent
TELEMETRY_FILE = DATA_DIR / "telemetry.json"
SENSORS_FILE = DATA_DIR / "sensors.json"
SHARED_BUS_FILE = DATA_DIR / "shared_bus.json"

def load_json(filepath):
    if not filepath.exists():
        return {}
    try:
        with open(filepath, 'r') as f:
            return json.load(f)
    except Exception:
        return {}

def status_color(value, limits):
    if value <= limits[0]:
        return Colors.RED
    elif value <= limits[1]:
        return Colors.YELLOW
    else:
        return Colors.GREEN

def format_timedelta(past_time):
    try:
        dt = datetime.fromisoformat(past_time)
        delta = datetime.now() - dt
        return f"{int(delta.total_seconds())}s ago"
    except Exception:
        return "n/a"

def render_header():
    return f"{Colors.BOLD}{Colors.CYAN}=== {loc.get_dual('system_monitor_title')} ==={Colors.RESET}\n"

def render_fsm(fsm_data):
    state = fsm_data.get("mode", "unknown")
    color = {
        "idle": Colors.YELLOW,
        "active": Colors.GREEN,
        "charging": Colors.CYAN,
        "error": Colors.RED
    }.get(state, Colors.GRAY)
    return (
        f"{Colors.BOLD}{loc.get_dual('fsm_state_label')}:{Colors.RESET}\n"
        f"  ▸ {loc.get('state_label', 'en')}: {color}{state.upper()}{Colors.RESET}\n"
    )

def render_telemetry(tele):
    battery = tele.get("battery_percent", 0)
    speed = tele.get("speed_mps", 0.0)
    impulse = tele.get("impulse_active", False)
    power = tele.get("power_wh", 0.0)
    consumption = tele.get("consumption_w", 0.0)
    bat_color = status_color(battery, (20, 60))
    return (
        f"{Colors.BOLD}{loc.get_dual('telemetry_label')}:{Colors.RESET}\n"
        f"  ▸ {loc.get_dual('battery_label')}: {bat_color}{battery:.1f}%{Colors.RESET}  {loc.get_dual('power_label')}: {power:.1f} Wh\n"
        f"  ▸ {loc.get_dual('speed_label')}: {speed:.2f} m/s  {loc.get_dual('consumption_label')}: {consumption:.1f} W\n"
        f"  ▸ {loc.get_dual('impulse_label')}: {'ACTIVE' if impulse else '—'}\n"
    )

def render_sensors(sens):
    prox_dist = sens.get("proximity", {}).get("docking_sensors", {}).get("front_distance", "n/a")
    core_temp_cpu = sens.get("thermal", {}).get("core_temp", {}).get("cpu", "n/a")
    comm_latency = "N/A" # Not directly available in new structure
    comm_rssi = sens.get("communication", {}).get("signal_strength_meters", {}).get("rssi", "n/a")
    imu_orientation_q = sens.get("navigation", {}).get("imu", {}).get("orientation_q", "n/a")

    return (
        f"{Colors.BOLD}{loc.get_dual('sensors_label')}:{Colors.RESET}\n"
        f"  ▸ {loc.get_dual('proximity_label')}: {prox_dist} cm   {loc.get_dual('core_temp_label')}: {core_temp_cpu} °C\n"
        f"  ▸ {loc.get_dual('comm_status_title')}: latency={comm_latency}ms  RSSI={comm_rssi} dB\n"
        f"  ▸ {loc.get_dual('imu_orientation_label')}: {imu_orientation_q}\n"
    )

def render_agents(shared):
    agents = shared if isinstance(shared, dict) else {}
    out = f"{Colors.BOLD}{loc.get_dual('agents_label')}:{Colors.RESET}\n"
    if not agents:
        out += f"  ({loc.get_dual('no_data_placeholder')})\n"
        return out
    for agent_id, props in agents.items():
        state = props.get("state", "n/a")
        last = props.get("last_update", "n/a")
        age = format_timedelta(last)
        col = status_color(0 if state == "error" else 100, (1, 50))
        out += f"  ▸ {agent_id}: {col}{state.upper()}{Colors.RESET}, {loc.get_dual('last_update_label')}: {age}\n"
    return out

def get_system_status(fsm, telemetry, sensors):
    if fsm.get("mode") == "error":
        return f"{Colors.RED}{loc.get_dual('status_critical')}{Colors.RESET}"
    if telemetry.get("battery_percent", 0) < 20:
        return f"{Colors.YELLOW}{loc.get_dual('status_warning')}{Colors.RESET}"
    # Removed communication latency check as 'latency_ms' is not directly available in the new sensor structure.
    return f"{Colors.GREEN}{loc.get_dual('status_stable')}{Colors.RESET}"

def main():
    fsm_client = FSMClient()
    try:
        while True:
            os.system('cls' if os.name == 'nt' else 'clear')
            fsm = fsm_client.get_state()
            telemetry = load_json(TELEMETRY_FILE)
            sensors = load_json(SENSORS_FILE)
            shared = load_json(SHARED_BUS_FILE)
            print(render_header())
            print(f"{loc.get_dual('status_label')}: {get_system_status(fsm, telemetry, sensors)}\n")
            print(render_fsm(fsm))
            print(render_telemetry(telemetry))
            print(render_sensors(sensors))
            print(render_agents(shared))
            print(f"\n{Colors.GRAY}{loc.get_dual('last_sync_label')}: {datetime.now().strftime('%H:%M:%S')}{Colors.RESET}")
            time.sleep(2)
    except KeyboardInterrupt:
        print(f"\n{loc.get_dual('exiting_monitor_message')}")

if __name__ == "__main__":
    main()