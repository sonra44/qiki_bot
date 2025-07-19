import json
import os
import time
from datetime import datetime
import sys

# Add project root to sys.path for imports
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(project_root)

from core.file_paths import TELEMETRY_FILE, SENSORS_FILE

# --- CONFIGURATION ---
REFRESH_INTERVAL = 2 # seconds

# ANSI color codes
COLOR_RESET = "\033[0m"
COLOR_CYAN = "\033[96m"
COLOR_MAGENTA = "\033[95m"

# --- HELPER FUNCTIONS ---

def clear_screen():
    """Clears the terminal screen."""
    os.system('cls' if os.name == 'nt' else 'clear')

def read_json_file(filepath: str) -> dict:
    """Safely reads a JSON file."""
    if not os.path.exists(filepath):
        return {"error": f"⚠️  {os.path.basename(filepath)} not found"}
    try:
        with open(filepath, 'r') as f:
            content = f.read()
            if not content.strip():
                return {"error": f"⚠️  {os.path.basename(filepath)} is empty"}
            data = json.loads(content)
            return data
    except (json.JSONDecodeError, IOError) as e:
        return {"error": f"⚠️  Error reading {os.path.basename(filepath)}: {e}"}

# --- MAIN DISPLAY FUNCTION ---

def display_navigation_monitor():
    """Renders and displays the navigation monitor HUD."""
    clear_screen()
    hud_lines = []
    width = 80

    hud_lines.append("╔" + "═" * ((width - 21) // 2) + " NAVIGATION MONITOR " + "═" * ((width - 21) // 2) + "╗")

    telemetry_data = read_json_file(TELEMETRY_FILE)
    sensors_data = read_json_file(SENSORS_FILE)

    # Check for errors in reading files
    if "error" in telemetry_data:
        hud_lines.append(f"║ {COLOR_MAGENTA}{telemetry_data['error']}{COLOR_RESET}".ljust(width - 1) + "║")
    if "error" in sensors_data:
        hud_lines.append(f"║ {COLOR_MAGENTA}{sensors_data['error']}{COLOR_RESET}".ljust(width - 1) + "║")

    # Extract data
    # Telemetry
    velocity = telemetry_data.get("velocity", 0.0)
    acceleration = telemetry_data.get("acceleration", 0.0)
    impulse_active = "ON" if telemetry_data.get("impulse_active", False) else "OFF"

    # Sensors (IMU and Gyro)
    imu = sensors_data.get("navigation", {}).get("imu", {})
    pitch = imu.get("pitch", 0.0)
    roll = imu.get("roll", 0.0)
    yaw = imu.get("yaw", 0.0)
    acc_x = imu.get("acc_x", 0.0)
    acc_y = imu.get("acc_y", 0.0)
    acc_z = imu.get("acc_z", 0.0)

    gyro = sensors_data.get("navigation", {}).get("gyroscope", {})
    angular_vel_x = gyro.get("angular_vel_x", 0.0)
    angular_vel_y = gyro.get("angular_vel_y", 0.0)
    angular_vel_z = gyro.get("angular_vel_z", 0.0)

    current_time_str = datetime.now().strftime("%H:%M:%S")

    # --- UI Assembly ---
    hud_lines.append("╠" + "═" * (width - 2) + "╣")
    hud_lines.append(f"║ {COLOR_CYAN}ORIENTATION / ОРИЕНТАЦИЯ{COLOR_RESET}".ljust(width - 1) + "║")
    hud_lines.append(f"║   Pitch / Тангаж: {pitch:>8.2f}°                                        ║")
    hud_lines.append(f"║   Roll / Крен: {roll:>10.2f}°                                         ║")
    hud_lines.append(f"║   Yaw / Рыскание: {yaw:>9.2f}°                                        ║")
    hud_lines.append("╠" + "═" * (width - 2) + "╣")

    hud_lines.append(f"║ {COLOR_CYAN}ACCELERATION / УСКОРЕНИЕ{COLOR_RESET}".ljust(width - 1) + "║")
    hud_lines.append(f"║   Acc X: {acc_x:>8.2f} m/s²                                         ║")
    hud_lines.append(f"║   Acc Y: {acc_y:>8.2f} m/s²                                         ║")
    hud_lines.append(f"║   Acc Z: {acc_z:>8.2f} m/s²                                         ║")
    hud_lines.append("╠" + "═" * (width - 2) + "╣")

    hud_lines.append(f"║ {COLOR_CYAN}ANGULAR VELOCITY / УГЛОВАЯ СКОРОСТЬ{COLOR_RESET}".ljust(width - 1) + "║")
    hud_lines.append(f"║   Angular Vel X: {angular_vel_x:>8.4f} rad/s                             ║")
    hud_lines.append(f"║   Angular Vel Y: {angular_vel_y:>8.4f} rad/s                             ║")
    hud_lines.append(f"║   Angular Vel Z: {angular_vel_z:>8.4f} rad/s                             ║")
    hud_lines.append("╠" + "═" * (width - 2) + "╣")

    hud_lines.append(f"║ {COLOR_CYAN}MOVEMENT / ДВИЖЕНИЕ{COLOR_RESET}".ljust(width - 1) + "║")
    hud_lines.append(f"║   Velocity / Скорость: {velocity:>8.2f} m/s                             ║")
    hud_lines.append(f"║   Acceleration / Ускорение: {acceleration:>8.2f} m/s²                         ║")
    hud_lines.append(f"║   Impulse Active / Импульс активен: {impulse_active:<5}                      ║")
    hud_lines.append("╚" + "═" * (width - 2) + "╝")

    hud_lines.append(f"\nTimestamp / Время: {current_time_str}")
    hud_lines.append("Press Ctrl+C to exit / Нажмите Ctrl+C для выхода...")

    print("\n".join(hud_lines))

# --- MAIN EXECUTION LOOP ---
if __name__ == "__main__":
    print("Starting Navigation Monitor. Press Ctrl+C to exit.")
    try:
        while True:
            display_navigation_monitor()
            time.sleep(REFRESH_INTERVAL)
    except KeyboardInterrupt:
        clear_screen()
        print("Navigation Monitor terminated by user.")