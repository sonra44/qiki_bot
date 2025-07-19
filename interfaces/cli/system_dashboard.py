

import os
import json
import time
import datetime
import math
import sys

# Add project root to sys.path for imports
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if project_root not in sys.path:
    sys.sys.path.append(project_root)

from core.fsm_client import FSMClient

# --- CONFIGURATION ---
TELEMETRY_FILE = os.path.join(project_root, "telemetry.json")
SENSORS_FILE = os.path.join(project_root, "sensors.json")

# ANSI color codes
COLOR_RED = "\033[91m"
COLOR_GREEN = "\033[92m"
COLOR_YELLOW = "\033[93m"
COLOR_RESET = "\033[0m"

# --- HELPER FUNCTIONS ---

def clear_screen():
    """Clears the terminal screen."""
    os.system('cls' if os.name == 'nt' else 'clear')

def read_data(filepath: str) -> dict:
    """
    Safely reads a JSON file.
    Returns: data_dict or empty dict if error/not found.
    """
    if not os.path.exists(filepath):
        return {}
    try:
        with open(filepath, 'r') as f:
            content = f.read()
            if not content.strip():
                return {}
            data = json.loads(content)
            return data
    except (json.JSONDecodeError, IOError):
        return {}def get_risk_level(temperature: float, distance: float) -> str:
    """Determines risk level based on temperature and distance."""
    if temperature > 90 or distance < 50:
        return f"{COLOR_RED}HIGH{COLOR_RESET}"
    elif temperature > 70 or distance < 100:
        return f"{COLOR_YELLOW}NORMAL{COLOR_RESET}"
    else:
        return f"{COLOR_GREEN}LOW{COLOR_RESET}"

def display_dashboard():
    clear_screen()
    hud_lines = []
    width = 80
    fsm_client = FSMClient()

    hud_lines.append("╔" + "═" * ((width - 17) // 2) + " SYSTEM DASHBOARD " + "═" * ((width - 17) // 2) + "╗")

    fsm_data = fsm_client.get_state()
    telemetry_data = read_data(TELEMETRY_FILE)
    sensors_data = read_data(SENSORS_FILE)

    # --- System Monitor Section ---
    hud_lines.append("╠" + "═" * (width - 2) + "╣")
    hud_lines.append(f"║ {COLOR_GREEN}SYSTEM MONITOR / СИСТЕМНЫЙ МОНИТОР{COLOR_RESET}".ljust(width - 1) + "║")
    hud_lines.append("╠" + "═" * (width - 2) + "╣")

    fsm_state = fsm_data.get("mode", "UNKNOWN")
    battery_pct = telemetry_data.get("battery_percent", 0.0)
    power_w = telemetry_data.get("consumption_w", 0.0)
    speed_mps = telemetry_data.get("velocity", 0.0)
    acceleration = telemetry_data.get("acceleration", 0.0)

    hud_lines.append(f"║ FSM State / Состояние FSM: {fsm_state.upper():<15} Battery / Батарея: {battery_pct:.1f}% ║")
    hud_lines.append(f"║ Power / Мощность: {power_w:.1f} W Speed / Скорость: {speed_mps:.2f} m/s Accel: {acceleration:.2f} m/s² ║")

    # Communication data
    comm_rssi = sensors_data.get("communication", {}).get("signal_strength_meters", {}).get("rssi", "N/A")
    comm_latency = "N/A" # Not directly available in new structure
    hud_lines.append(f"║ Comm: RSSI={comm_rssi} dB Latency={comm_latency} ms                                     ║")

    # --- Scan Report Section ---
    hud_lines.append("╠" + "═" * (width - 2) + "╣")
    hud_lines.append(f"║ {COLOR_GREEN}SCAN REPORT / ОТЧЕТ СКАНИРОВАНИЯ{COLOR_RESET}".ljust(width - 1) + "║")
    hud_lines.append("╠" + "═" * (width - 2) + "╣")

    # Simulate scan data if not present in sensors.json
    # In a real scenario, this would come from the RLSM cluster
    scan_objects = sensors_data.get("rlsm", {}).get("radar", {}).get("detected_objects", [])
    if not scan_objects:
        # Generate fictitious data if no real data is available
        scan_objects = [
            {"id": "OBJ-001", "distance": 150, "temperature": 60},
            {"id": "OBJ-002", "distance": 70, "temperature": 85},
            {"id": "OBJ-003", "distance": 30, "temperature": 100}
        ]

    for obj in scan_objects:
        obj_id = obj.get("id", "N/A")
        distance = obj.get("distance", 0)
        temperature = obj.get("temperature", 0)
        risk = get_risk_level(temperature, distance)
        hud_lines.append(f"║   {obj_id}: Dist={distance:<5}m Temp={temperature:<5}°C Risk={risk:<15} ║")

    hud_lines.append("╚" + "═" * (width - 2) + "╝")

    hud_lines.append(f"\nTimestamp / Время: {datetime.datetime.now().strftime('%H:%M:%S')}")
    hud_lines.append("Press Ctrl+C to exit / Нажмите Ctrl+C для выхода...")

    print("\n".join(hud_lines))

# --- MAIN EXECUTION LOOP ---
if __name__ == "__main__":
    print("Starting System Dashboard. Press Ctrl+C to exit.")
    try:
        while True:
            display_dashboard()
            time.sleep(2)
    except KeyboardInterrupt:
        clear_screen()
        print("System Dashboard terminated by user.")
