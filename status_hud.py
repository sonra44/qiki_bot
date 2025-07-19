import os
import json
import time
import datetime
from core.fsm_client import FSMClient

# --- CONFIGURATION ---
# File paths
TELEMETRY_FILE = "telemetry.json"
SENSORS_FILE = "sensors.json"
SHARED_BUS_FILE = "shared_bus.json"

# Static specifications (as real config files may not be available)
SPEC_MASS_KG = 35.0
SPEC_MAX_SPEED_MPS = 1.2
SPEC_POWER_CAPACITY_WH = 500.0
SPEC_ANTENNA_TYPE = "omni 2.4GHz"
SPEC_PROTOCOLS = ["WiFi", "LoRa"]

# ANSI color codes
COLOR_RED = "\033[91m"
COLOR_YELLOW = "\033[93m"
COLOR_GREEN = "\033[92m"
COLOR_BLUE = "\033[94m"
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

def make_bar(value: float, max_value: float, length: int = 14) -> str:
    """Creates an ASCII progress bar."""
    if max_value == 0: return f"[{('░' * length)}]" 
    value = max(0, min(value, max_value))
    fill_len = int((value / max_value) * length)
    empty_len = length - fill_len
    return f"[{('█' * fill_len)}{('░' * empty_len)}]" 

# --- MAIN DISPLAY FUNCTION ---

def display_cockpit_hud():
    """Renders and displays the entire cockpit HUD."""
    # --- Data Ingestion ---
    fsm_client = FSMClient()
    telemetry, tele_mod, tele_err = read_data(TELEMETRY_FILE)
    fsm = fsm_client.get_state()
    sensors, sens_mod, sens_err = read_data(SENSORS_FILE)
    shared_bus, bus_mod, bus_err = read_data(SHARED_BUS_FILE)


    # --- Data Extraction & Processing ---
    # Physics
    speed = telemetry.get("velocity", 0.0)
    accel = telemetry.get("acceleration", 0.0)
    impulse = telemetry.get("impulse_active", False)

    # Power
    battery_pct = telemetry.get("battery_percent", 0.0)
    power_w = telemetry.get("consumption_w", 0.0)
    current_wh = telemetry.get("power_wh", 0.0)

    # Comms
    # Communication data from new hierarchical sensors.json
    # Latency (latency_ms) is no longer directly available in the new structure.
    latency = "N/A" 
    rssi = sensors.get("communication", {}).get("signal_strength_meters", {}).get("rssi", -100)

    # FSM
        fsm_state = fsm.get("mode", "UNKNOWN")
    fsm_trigger = fsm_data.get("last_event", "N/A")
    agent_state = next(iter(shared_bus.values()), {}).get("state", "N/A") if shared_bus else "N/A"

    # Time
    local_time_str = datetime.datetime.now().strftime("%H:%M:%S")
    last_update_str = datetime.datetime.fromtimestamp(tele_mod).strftime("%H:%M:%S") if tele_mod else "N/A"

    # --- UI Assembly ---
    hud = []
    width = 80
    hud.append("╔" + "═" * (width - 2) + "╗")
    hud.append("║" + " QIKI BOT - COCKPIT STATUS / СТАТУС КОКПИТА ".center(width - 2) + "║")
    hud.append("╚" + "═" * (width - 2) + "╝")

    # Section: PHYSICS & POWER
    hud.append("┌─ ⚙️ PHYSICS / ФИЗИКА ─" + "─" * 21 + "┬─ ⚡ POWER / ПИТАНИЕ ──" + "─" * 21 + "┐")
    phys_line1 = f"  Mass / Масса: {SPEC_MASS_KG:.1f} kg".ljust(38)
    pwr_line1 = f"  Battery / Батарея: {battery_pct:.1f}%".ljust(39)
    hud.append(f"│{phys_line1}│{pwr_line1}│")

    phys_line2 = f"  Impulse / Импульс: {str(impulse)}".ljust(38)
    pwr_line2 = f"  {make_bar(battery_pct, 100)}".ljust(39)
    hud.append(f"│{phys_line2}│{pwr_line2}│")

    phys_line3 = f"  Speed / Скорость: {speed:.2f} m/s".ljust(38)
    pwr_line3 = f"  Power / Мощность: {power_w:.1f} W".ljust(39)
    hud.append(f"│{phys_line3}│{pwr_line3}│")

    phys_line4 = f"  Acceleration / Ускорение: {accel:.2f} m/s²".ljust(38)
    pwr_line4 = f"  Current / Текущий заряд: {current_wh:.1f} Wh".ljust(39)
    hud.append(f"│{phys_line4}│{pwr_line4}│")
    hud.append("├─" + "─" * 76 + "┤")

    # Section: COMM & FSM
    hud.append("│" + "  COMM / СВЯЗЬ".ljust(38) + "│" + "  FSM / СОСТОЯНИЕ".ljust(39) + "│")
    comm_line1 = f"  Antenna / Антенна: {SPEC_ANTENNA_TYPE}".ljust(38)
    fsm_color = COLOR_RED if fsm_state == "error" else COLOR_GREEN
    fsm_line1 = f"  State / Состояние: {fsm_color}{fsm_state.upper()}{COLOR_RESET}".ljust(38 + len(fsm_color) + len(COLOR_RESET))
    hud.append(f"│{comm_line1}│{fsm_line1}│")

    comm_line2 = f"  RSSI: {rssi} dB".ljust(20) + f"Latency / Задержка: {latency:.0f} ms".ljust(18)
    fsm_line2 = f"  Trigger / Событие: {fsm_trigger}".ljust(39)
    hud.append(f"│{comm_line2}│{fsm_line2}│")

    comm_line3 = f"  Protocols / Протоколы: {', '.join(SPEC_PROTOCOLS)}".ljust(38)
    diag_line = f"{COLOR_RED}⚠️ SYSTEM ERROR{COLOR_RESET}" if fsm_state == "error" else ""
    fsm_line3 = f"  Diagnostic / Диагностика: {diag_line}".ljust(39 + (len(COLOR_RED) + len(COLOR_RESET) if diag_line else 0))
    hud.append(f"│{comm_line3}│{fsm_line3}│")
    hud.append("├─" + "─" * 76 + "┤")

    # Section: TIME & ERRORS
    hud.append("│" + " ⏱️ TIME / ВРЕМЯ".ljust(38) + "│" + "  LOG / ОШИБКИ".ljust(39) + "│")
    time_line1 = f"  Local Time / Система: {local_time_str}".ljust(38)
    err_line1 = f"  {tele_err or sens_err or '- OK -'}".ljust(39)
    hud.append(f"│{time_line1}│{err_line1}│")

    time_line2 = f"  Last Telemetry Update / Обновление: {last_update_str}".ljust(38)
    err_line2 = f"  {fsm_err or bus_err or '- OK -'}".ljust(39)
    hud.append(f"│{time_line2}│{err_line2}│")

    hud.append("└" + "─" * 76 + "┘")
    hud.append("Press Ctrl+C to exit / Нажмите Ctrl+C для выхода...")

    clear_screen()
    print("\n".join(hud))

# --- MAIN EXECUTION LOOP ---
if __name__ == "__main__":
    # Start the cache watcher in the background
    json_cache.start_cache_watcher()
    try:
        while True:
            display_cockpit_hud()
            time.sleep(1) # Can be faster now
    except KeyboardInterrupt:
        clear_screen()
        print("Cockpit HUD terminated by user.")
    finally:
        json_cache.stop_cache_watcher()