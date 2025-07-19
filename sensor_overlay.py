import os
import json
import time
import datetime
import sys

# Add project root to sys.path for imports
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.append(project_root)

from core.localization_manager import loc
from core.file_paths import SENSORS_FILE

# ANSI color codes
COLOR_RED = "\033[91m"
COLOR_YELLOW = "\033[93m"
COLOR_RESET = "\033[0m"

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def read_sensors_data(filepath: str) -> dict:
    if not os.path.exists(filepath):
        return {"error": f"⚠️  {os.path.basename(filepath)} not found"}
    try:
        with open(filepath, 'r') as f:
            content = f.read()
            if not content.strip():
                return {"error": f"⚠️  {os.path.basename(filepath)} is empty"}
            return json.loads(content)
    except (json.JSONDecodeError, IOError) as e:
        return {"error": f"⚠️  Error reading {os.path.basename(filepath)}: {e}"}

def format_section(title_key: str, content_lines: list, width: int = 78) -> list:
    lines = []
    title = loc.get_dual(title_key)
    lines.append("╔" + "═" * (width - 2) + "╗")
    lines.append(f"║ {title.ljust(width - 4)} ║")
    lines.append("╠" + "═" * (width - 2) + "╣")
    for line in content_lines:
        lines.append(f"║ {line.ljust(width - 4)} ║")
    lines.append("╚" + "═" * (width - 2) + "╝")
    return lines

def display_sensor_overlay():
    sensors_data = read_sensors_data(SENSORS_FILE)
    hud_lines = []
    width = 80

    hud_lines.append("╔" + "═" * (width - 2) + "╗")
    hud_lines.append("║" + loc.get_dual('sensor_overlay_title').center(width - 2) + "║")
    hud_lines.append("╚" + "═" * (width - 2) + "╝")

    if "error" in sensors_data:
        hud_lines.append(f"\n{COLOR_RED}{sensors_data['error']}{COLOR_RESET}\n")
    else:
        # IMU Section
        imu = sensors_data.get("navigation", {}).get("imu", {})
        imu_content = [
            f"  {loc.get_dual('accel_x_label')}: {imu.get('acc_x', 0.0):>7.2f}",
            f"  {loc.get_dual('accel_y_label')}: {imu.get('acc_y', 0.0):>7.2f}",
            f"  {loc.get_dual('accel_z_label')}: {imu.get('acc_z', 0.0):>7.2f}",
            f"  {loc.get_dual('pitch_label')}: {imu.get('pitch', 0.0):>8.2f}°",
            f"  {loc.get_dual('roll_label')}: {imu.get('roll', 0.0):>9.2f}°",
            f"  {loc.get_dual('yaw_label')}: {imu.get('yaw', 0.0):>8.1f}°"
        ]
        if not imu: imu_content = [f"{COLOR_YELLOW}⚠️ {loc.get_dual('sensor_data_missing')}: IMU{COLOR_RESET}"]
        hud_lines.extend(format_section("imu_section_title", imu_content, width=width))
        hud_lines.append("\n")

        # Other sensors...

    hud_lines.append("\n" + "═" * width)
    hud_lines.append(f"{loc.get_dual('local_time_label')}: {datetime.datetime.now().strftime("%H:%M:%S")}")
    hud_lines.append(loc.get_dual('exit_message'))

    clear_screen()
    print("\n".join(hud_lines))

if __name__ == "__main__":
    try:
        while True:
            display_sensor_overlay()
            time.sleep(2)
    except KeyboardInterrupt:
        clear_screen()
        print(loc.get_dual('terminated_by_user_message'))
