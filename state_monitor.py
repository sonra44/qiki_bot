

import os
import json
import time
import datetime
from collections import deque
from core.fsm_client import FSMClient

# --- CONFIGURATION ---
RULES_FILE = "config/rules.json"
TELEMETRY_FILE = "telemetry.json"
SENSORS_FILE = "sensors.json"

# ANSI color codes
COLOR_RED = "\033[91m"
COLOR_GREEN = "\033[92m"
COLOR_YELLOW = "\033[93m"
COLOR_BLUE = "\033[94m"
COLOR_RESET = "\033[0m"

# --- GLOBAL STATE FOR EVENT LOG ---
# This will store events in memory for the duration of the script's run
EVENT_LOG = deque(maxlen=7) # Keep last 7 events
LAST_FSM_STATE = ""

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
        return {}, 0, f"⚠️  Error reading {os.path.basename(filepath)}: {e}"

def _get_value_from_path(data: dict, path: str):
    """Helper to get a nested value from a dictionary using dot notation."""
    parts = path.split('.')
    current_data = data
    for part in parts:
        if isinstance(current_data, dict) and part in current_data:
            current_data = current_data[part]
        else:
            return None # Path not found
    return current_data

def _evaluate_single_condition(condition_str: str, data_context: dict) -> bool:
    """Safely evaluates a single comparison condition (e.g., 'field < value')."""
    operators = {'>': lambda a, b: a > b, '<': lambda a, b: a < b, '==': lambda a, b: a == b,
                 '!=': lambda a, b: a != b, '>=': lambda a, b: a >= b, '<=': lambda a, b: a <= b}

    op = None
    for operator_str in sorted(operators.keys(), key=len, reverse=True):
        if operator_str in condition_str:
            parts = condition_str.split(operator_str, 1)
            if len(parts) == 2:
                field_path = parts[0].strip()
                value_str = parts[1].strip()
                op = operator_str
                break
    
    if not op:
        return False

    actual_value = _get_value_from_path(data_context, field_path)
    if actual_value is None:
        return False

    try:
        if isinstance(actual_value, (int, float)):
            target_value = float(value_str)
        elif isinstance(actual_value, bool):
            target_value = value_str.lower() == 'true'
        else:
            target_value = value_str.strip("'\"")
    except ValueError:
        return False

    return operators[op](actual_value, target_value)

def _evaluate_complex_condition(condition_str: str, data_context: dict) -> bool:
    """Evaluates complex conditions with 'and'/'or' operators."""
    if " and " in condition_str:
        sub_conditions = condition_str.split(" and ")
        return all(_evaluate_single_condition(sub.strip(), data_context) for sub in sub_conditions)
    elif " or " in condition_str:
        sub_conditions = condition_str.split(" or ")
        return any(_evaluate_single_condition(sub.strip(), data_context) for sub in sub_conditions)
    else:
        return _evaluate_single_condition(condition_str, data_context)

# --- MAIN DISPLAY FUNCTION ---

def display_state_monitor():
    global LAST_FSM_STATE, EVENT_LOG

    # --- Data Ingestion ---
    fsm_client = FSMClient()
    fsm = fsm_client.get_state()
    rules_data, rules_mod, rules_err = read_data(RULES_FILE)
    telemetry, tele_mod, tele_err = read_data(TELEMETRY_FILE)
    sensors, sens_mod, sens_err = read_data(SENSORS_FILE)

    # --- Data Extraction & Processing ---
        current_fsm_state = fsm.get("mode", "UNKNOWN")
    fsm_timestamp = datetime.datetime.now().strftime("%H:%M:%S") # Use current time for display

    # Update Event Log
    if current_fsm_state != LAST_FSM_STATE and LAST_FSM_STATE != "":
        EVENT_LOG.append(f"[{fsm_timestamp}] {LAST_FSM_STATE} → {current_fsm_state}")
    LAST_FSM_STATE = current_fsm_state

    # Data context for rule evaluation
    data_context = {
        "telemetry": telemetry,
        "sensors": sensors,
        "fsm": {"state": current_fsm_state}
    }

    # --- UI Assembly ---
    hud_lines = []
    width = 80

    hud_lines.append("╔" + "═" * (width - 2) + "╗")
    hud_lines.append("║" + " QIKI BOT - FSM & DECISION CORE ".center(width - 2) + "║")
    hud_lines.append("╚" + "═" * (width - 2) + "╝")

    # Section: FSM State
    hud_lines.append("┌─ 🧠 FSM STATE / СОСТОЯНИЕ АВТОМАТА ─" + "─" * 35 + "┐")
    fsm_color = COLOR_RED if current_fsm_state == "error" else COLOR_GREEN
    hud_lines.append(f"│ Current State / Текущее состояние: {fsm_color}{current_fsm_state.upper():<10}{COLOR_RESET} │")
    hud_lines.append(f"│ Last Event / Последнее событие: {'N/A':<20} │") # FSM doesn't store last event directly
    hud_lines.append(f"│ Timestamp / Время: {fsm_timestamp:<20} │")
    hud_lines.append("├─" + "─" * (width - 2) + "┤")

    # Section: Active Rules
    hud_lines.append("│ ⚙️ ACTIVE RULES / АКТИВНЫЕ ПРАВИЛА ─" + "─" * 40 + "│")
    if rules_err:
        hud_lines.append(f"│ {COLOR_RED}{rules_err:<74}{COLOR_RESET} │")
    elif not rules_data:
        hud_lines.append(f"│ {COLOR_YELLOW}No rules loaded or rules.json is empty.{COLOR_RESET:<68} │")
    else:
        for rule in rules_data:
            rule_name = rule.get('name', 'Unnamed Rule')
            condition_str = rule.get('condition', 'True')
            action = rule.get('action', 'N/A')
            
            status_char = "[ ]"
            try:
                if _evaluate_complex_condition(condition_str, data_context):
                    status_char = f"[{COLOR_GREEN}✓{COLOR_RESET}]"
                else:
                    status_char = f"[{COLOR_YELLOW} {COLOR_RESET}]" # Pending
            except Exception:
                status_char = f"[{COLOR_RED}X{COLOR_RESET}]" # Error evaluating

            rule_line = f" {status_char} {rule_name} → {action}"
            hud_lines.append(f"│ {rule_line:<74} │")
    hud_lines.append("├─" + "─" * (width - 2) + "┤")

    # Section: Event Log
    hud_lines.append("│ 📜 EVENT LOG / ЖУРНАЛ СОБЫТИЙ ─" + "─" * 44 + "│")
    if not EVENT_LOG:
        hud_lines.append(f"│ {COLOR_YELLOW}No events yet.{COLOR_RESET:<74} │")
    else:
        for event_entry in EVENT_LOG:
            hud_lines.append(f"│ {event_entry:<74} │")
    hud_lines.append("├─" + "─" * (width - 2) + "┤")

    # Section: Anomalies
    hud_lines.append("│ ⚠️ ANOMALIES / АНОМАЛИИ ─" + "─" * 50 + "│")
    anomalies_found = False
    if telemetry.get("battery_percent", 100) < 10:
        hud_lines.append(f"│ {COLOR_RED}⚠️ LOW POWER / НИЗКИЙ ЗАРЯД БАТАРЕИ{COLOR_RESET:<60} │")
        anomalies_found = True
    if sensors.get("navigation", {}).get("imu", {}).get("accel_z", 0) < -1.0:
        hud_lines.append(f"│ {COLOR_RED}⚠️ FALL DETECTED / ОБНАРУЖЕНО ПАДЕНИЕ{COLOR_RESET:<60} │")
        anomalies_found = True
    if sensors.get("navigation", {}).get("gyroscope", {}).get("yaw_rate", 0) > 0.5:
        hud_lines.append(f"│ {COLOR_RED}⚠️ HIGH YAW RATE / ВЫСОКАЯ СКОРОСТЬ РЫСКАНИЯ{COLOR_RESET:<60} │")
        anomalies_found = True
    
    if not anomalies_found:
        hud_lines.append(f"│ {COLOR_GREEN}No anomalies detected. / Аномалий не обнаружено.{COLOR_RESET:<74} │")

    # FSM Error Reason
    if current_fsm_state == "error" and anomalies_found:
        hud_lines.append(f"│ {COLOR_RED}FSM ERROR REASON: See anomalies above.{COLOR_RESET:<74} │")
    elif current_fsm_state == "error":
        hud_lines.append(f"│ {COLOR_RED}FSM ERROR: Reason unknown or not detected by monitor.{COLOR_RESET:<74} │")

    hud_lines.append("└" + "─" * (width - 2) + "┘")

    # Footer
    hud_lines.append(f"\nLocal Time / Локальное время: {datetime.datetime.now().strftime("%H:%M:%S")}")
    hud_lines.append("Press Ctrl+C to exit / Нажмите Ctrl+C для выхода...")

    clear_screen()
    print("\n".join(hud_lines))

# --- MAIN EXECUTION LOOP ---
if __name__ == "__main__":
    # Start the cache watcher in the background
    json_cache.start_cache_watcher()
    try:
        while True:
            display_state_monitor()
            time.sleep(1) # Can be faster now
    except KeyboardInterrupt:
        clear_screen()
        print("FSM & Decision Core Monitor terminated by user.")
    finally:
        json_cache.stop_cache_watcher()
