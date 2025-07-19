import os
import json
import time
import datetime

# --- CONFIGURATION ---
TELEMETRY_FILE = "telemetry.json"

# ANSI color codes
COLOR_RED = "\033[91m"
COLOR_GREEN = "\033[92m"
COLOR_YELLOW = "\033[93m"
COLOR_RESET = "\033[0m"

# --- HELPER FUNCTIONS ---

def clear_screen():
    """Clears the terminal screen."""
    os.system('cls' if os.name == 'nt' else 'clear')

def read_data(filepath: str) -> (dict, float, str):
    """
    Safely reads a JSON file.
    Returns: (data_dict, last_modified_timestamp, error_string)
    """
    if not os.path.exists(filepath):
        return {}, 0, f"⚠️  {os.path.basename(filepath)} not found"
    try:
        last_mod_time = os.path.getmtime(filepath)
        with open(filepath, 'r') as f:
            content = f.read()
            if not content.strip():
                return {}, last_mod_time, f"⚠️  {os.path.basename(filepath)} is empty"
            data = json.loads(content)
            return data, last_mod_time, ""
    except (json.JSONDecodeError, IOError) as e:
        return {}, 0, f"⚠️  Error reading {os.path.basename(filepath)}"

def format_value(value, unit="", precision=2, missing_msg="N/A"):
    """Formats a numerical value or returns a missing message."""
    if value is None:
        return missing_msg
    if isinstance(value, bool):
        return f"{COLOR_GREEN}✅ YES{COLOR_RESET}" if value else "❌ NO"
    return f"{value:>{precision}.{precision}f}{unit}"

# --- MAIN DISPLAY FUNCTION ---

def display_power_hud():
    """Renders and displays the power core HUD."""
    telemetry, tele_mod, tele_err = read_data(TELEMETRY_FILE)

    # --- Data Extraction & Processing ---
    battery_percent = telemetry.get("battery_percent")
    power_wh = telemetry.get("power_wh")
    consumption_w = telemetry.get("consumption_w")
    speed_mps = telemetry.get("speed_mps")
    velocity = telemetry.get("velocity")
    acceleration = telemetry.get("acceleration")
    impulse_active = telemetry.get("impulse_active")

    # Placeholder for voltage/current (not in telemetry.json, but requested)
    battery_voltage = 14.8 # Example static value
    battery_current = 3.2  # Example static value
    battery_health = "✅ GOOD"

    # Calculate efficiency (example: power_out / power_in)
    # This is a placeholder as we don't have power_in/out in telemetry.json
    efficiency = 88.2 # Example static value

    # --- UI Assembly ---
    hud_lines = []
    width = 80

    hud_lines.append("╔" + "═" * (width - 2) + "╗")
    hud_lines.append("║" + " QIKI BOT - POWER CORE / ЭНЕРГЕТИЧЕСКОЕ ЯДРО ".center(width - 2) + "║")
    hud_lines.append("╚" + "═" * (width - 2) + "╝")

    # Section: Battery Status
    hud_lines.append("┌─ 🔋 BATTERY STATUS / СОСТОЯНИЕ БАТАРЕИ ─" + "─" * 33 + "┐")
    charge_line = f"  Charge / Заряд: {format_value(battery_percent, '%')}"
    if battery_percent is not None and battery_percent < 15:
        charge_line += f" {COLOR_RED}⚠️ LOW BATTERY / НИЗКИЙ ЗАРЯД БАТАРЕИ{COLOR_RESET}"
    hud_lines.append(f"│ {charge_line.ljust(width - 4)} │")

    hud_lines.append(f"│ Power / Мощность: {format_value(power_wh, ' Wh').ljust(width - 20)} │")
    hud_lines.append(f"│ Voltage / Напряжение: {format_value(battery_voltage, ' V').ljust(width - 24)} │")
    hud_lines.append(f"│ Current / Ток: {format_value(battery_current, ' A').ljust(width - 18)} │")
    hud_lines.append(f"│ Health / Здоровье: {battery_health.ljust(width - 20)} │")
    hud_lines.append("├─" + "─" * (width - 2) + "┤")

    # Section: Power Flow
    hud_lines.append("│ ⚡ POWER FLOW / ПОТОК ЭНЕРГИИ ─" + "─" * 44 + "│")
    hud_lines.append(f"│ Consumption / Потребление: {format_value(consumption_w, ' W').ljust(width - 28)} │")
    hud_lines.append(f"│ Efficiency / Эффективность: {format_value(efficiency, ' %').ljust(width - 30)} │")
    hud_lines.append(f"│ Acceleration / Ускорение: {format_value(acceleration, ' m/s²').ljust(width - 28)} │")
    hud_lines.append(f"│ Speed / Скорость: {format_value(speed_mps, ' m/s').ljust(width - 20)} │")
    hud_lines.append("├─" + "─" * (width - 2) + "┤")

    # Section: Impulse & Drive
    hud_lines.append("│ 🚀 IMPULSE & DRIVE / ИМПУЛЬС И ПРИВОД ─" + "─" * 36 + "│")
    impulse_status = format_value(impulse_active, missing_msg="N/A")
    hud_lines.append(f"│ Impulse Active / Импульс активен: {impulse_status.ljust(width - 35)} │")
    hud_lines.append(f"│ Velocity / Скорость: {format_value(velocity, ' m/s').ljust(width - 22)} │")
    hud_lines.append(f"│ Kinetic Mode / Режим движения: {'CRUISE'.ljust(width - 30)} │") # Static for now
    hud_lines.append("└" + "─" * (width - 2) + "┘")

    # Footer
    hud_lines.append(f"\nLocal Time / Локальное время: {datetime.datetime.now().strftime("%H:%M:%S")}")
    hud_lines.append(f"Last Telemetry Update / Обновление: {datetime.datetime.fromtimestamp(tele_mod).strftime("%H:%M:%S") if tele_mod else "N/A"}")
    if tele_err: hud_lines.append(f"{COLOR_RED}{tele_err}{COLOR_RESET}")
    hud_lines.append("Press Ctrl+C to exit / Нажмите Ctrl+C для выхода...")

    clear_screen()
    print("\n".join(hud_lines))

# --- MAIN EXECUTION LOOP ---
if __name__ == "__main__":
    try:
        while True:
            display_power_hud()
            time.sleep(2)
    except KeyboardInterrupt:
        clear_screen()
        print("Power Core HUD terminated by user.")