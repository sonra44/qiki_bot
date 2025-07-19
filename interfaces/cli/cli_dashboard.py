import os
import json
import time
import datetime
import sys

# Add project root to sys.path for imports
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.append(project_root)

from core.file_paths import FSM_STATE_FILE, TELEMETRY_FILE, SENSORS_FILE
from core.agent_profile import AgentProfileManager # Import the new AgentProfileManager

# --- Helper Functions ---
def clear_screen():
    """Clears the terminal screen."""
    os.system('cls' if os.name == 'nt' else 'clear')

def read_json_file(filepath: str, default_data: dict) -> dict:
    """Safely reads a JSON file, returning default data if file is missing or corrupt."""
    if not os.path.exists(filepath):
        # print(f"[WARN] File not found: {filepath}. Using default data.") # Suppress for dashboard
        return default_data
    try:
        with open(filepath, 'r') as f:
            content = f.read()
            if not content.strip():
                # print(f"[WARN] File empty: {filepath}. Using default data.") # Suppress for dashboard
                return default_data
            data = json.loads(content)
            return data
    except json.JSONDecodeError as e:
        # print(f"[ERROR] Corrupt JSON in {filepath}: {e}. Using default data.") # Suppress for dashboard
        return default_data
    except Exception as e:
        # print(f"[ERROR] Unexpected error reading {filepath}: {e}. Using default data.") # Suppress for dashboard
        return default_data

def format_section(title_en: str, title_ru: str, content_lines: list, width: int = 78) -> list:
    """Formats a section with an ASCII frame and dual-language title."""
    lines = []
    lines.append("╔" + "═" * (width - 2) + "╗")
    lines.append(f"║ {title_en.ljust(width - 4)} ║")
    lines.append(f"║ {title_ru.ljust(width - 4)} ║")
    lines.append("╠" + "═" * (width - 2) + "╣")
    for line in content_lines:
        lines.append(f"║ {line.ljust(width - 4)} ║")
    lines.append("╚" + "═" * (width - 2) + "╝")
    return lines

def _format_sensor_data_recursive(data: dict, indent: int = 0) -> list:
    formatted_lines = []
    indent_str = "  " * indent
    for key, value in data.items():
        if isinstance(value, dict):
            formatted_lines.append(f"{indent_str}{key.replace('_', ' ').title()}:")
            formatted_lines.extend(_format_sensor_data_recursive(value, indent + 1))
        else:
            formatted_lines.append(f"{indent_str}{key.replace('_', ' ').title()}: {value}")
    return formatted_lines

def display_dashboard():
    """Reads data from JSON files and displays the cockpit interface."""
    clear_screen()

    # --- Load Data ---
    fsm_state_data = read_json_file(FSM_STATE_FILE, {"state": "unknown"})
    telemetry_data = read_json_file(TELEMETRY_FILE, {
        "battery_percent": 0.0,
        "power_wh": 0.0,
        "speed_mps": 0.0,
        "consumption_w": 0.0,
        "velocity": 0.0,
        "acceleration": 0.0,
        "impulse_active": False
    })
    sensors_data = read_json_file(SENSORS_FILE, {
        "comm_ping": {"latency_ms": 0.0, "rssi_db": 0},
        "gyro": {"angular_vel_x": 0.0, "angular_vel_y": 0.0, "angular_vel_z": 0.0, "drift": 0.0},
        "imu": {"acc_x": 0.0, "acc_y": 0.0, "acc_z": 0.0, "pitch": 0.0, "roll": 0.0, "yaw": 0.0},
        "magnetometer": {"field_strength": 0.0},
        "proximity": 0.0,
        "thermo_cam": 0.0
    })
    
    agent_manager = AgentProfileManager()
    shared_bus_agents = agent_manager.all_agents() # Get agents as a dictionary

    # --- Prepare Sections ---
    # FSM State
    fsm_content = [
        f"Current State / Текущее состояние: {fsm_state_data.get('state', 'N/A').upper()}"
    ]

    # Power System
    power_content = [
        f"Battery / Батарея: {telemetry_data.get('battery_percent', 0.0):.1f}%",
        f"Power (Wh) / Мощность (Вт*ч): {telemetry_data.get('power_wh', 0.0):.1f}",
        f"Consumption (W) / Потребление (Вт): {telemetry_data.get('consumption_w', 0.0):.1f}"
    ]

    # Motion
    motion_content = [
        f"Velocity (m/s) / Скорость (м/с): {telemetry_data.get('velocity', 0.0):.2f}",
        f"Acceleration (m/s²) / Ускорение (м/с²): {telemetry_data.get('acceleration', 0.0):.2f}",
        f"Impulse Active / Импульс активен: {telemetry_data.get('impulse_active', False)}"
    ]

    # Sensors
    sensors_content = _format_sensor_data_recursive(sensors_data)

    # Shared Bus (Agents)
    shared_bus_content = []
    if shared_bus_agents:
        for agent_id, agent_data in shared_bus_agents.items():
            shared_bus_content.append(f"Agent '{agent_id}' / Агент '{agent_id}':")
            shared_bus_content.append(f"  State / Состояние: {agent_data.get('state', 'N/A')}")
            shared_bus_content.append(f"  Battery / Батарея: {agent_data.get('battery', 0.0):.1f}%")
            shared_bus_content.append(f"  Location / Позиция: {agent_data.get('position', [0,0])}")
            shared_bus_content.append(f"  Last Update / Последнее обновление: {agent_data.get('last_update', 'N/A')}")
    else:
        shared_bus_content.append("No agents found in shared bus.")

    # --- Display Sections ---
    print(f"QIKI Bot Cockpit Interface - {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)

    print("\n".join(format_section("FSM STATE", "СОСТОЯНИЕ FSM", fsm_content)))
    print("\n")
    print("\n".join(format_section("POWER SYSTEM", "ЭНЕРГОСИСТЕМА", power_content)))
    print("\n")
    print("\n".join(format_section("MOTION", "ДВИЖЕНИЕ", motion_content)))
    print("\n")
    print("\n".join(format_section("SENSORS", "СЕНСОРЫ", sensors_content)))
    print("\n")
    print("\n".join(format_section("SHARED BUS", "ОБЩАЯ ШИНА", shared_bus_content)))

    print("\n" + "=" * 80)
    print("Controls: [Q] Quit / Выйти | [R] Refresh / Обновить (Press Enter after Q/R)")

# --- Main Loop ---
if __name__ == "__main__":
    try:
        while True:
            display_dashboard()

            # Simple blocking input for Q/R
            # sys.stdin.readline() blocks until Enter is pressed
            sys.stdout.write("\nWaiting for input... ")
            sys.stdout.flush()
            key = sys.stdin.readline().strip()
            if key.lower() == 'q':
                break
            elif key.lower() == 'r':
                pass # Refresh happens on next iteration

            time.sleep(2) # Update every 2 seconds

    except KeyboardInterrupt:
        print("\nDashboard interrupted by user.")
    except Exception as e:
        print(f"\n[CRITICAL ERROR] An unexpected error occurred: {e}")
    finally:
        clear_screen()
        print("Dashboard terminated.")