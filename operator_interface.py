import json
import os
import shlex
import time
import sys
from datetime import datetime, timedelta

# Add project root to sys.path for imports
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(project_root)

from core.file_paths import TELEMETRY_FILE, FSM_STATE_FILE, MISSION_STATUS_FILE, SHARED_BUS_FILE, RULES_FILE, QIKI_BOOT_LOG_FILE
from core.fsm_client import FSMClient
from core.fsm_io import enqueue_event
from core.shared_bus_manager import SharedBusManager
from core.localization_manager import LocalizationManager

# --- Constants ---
CLI_INPUT_LOG_FILE = os.path.join(project_root, 'logs', 'cli_input.log')

# --- Localization Manager ---
loc = LocalizationManager()

# --- File Utilities ---
def read_json_file(file_path, default_val={}):
    if not os.path.exists(file_path) or os.path.getsize(file_path) == 0:
        return default_val
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return default_val

# --- Logging ---
def _log_to_file(msg, level):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(CLI_INPUT_LOG_FILE, 'a') as f:
        f.write(f"[{timestamp}] [{level}] {msg}\n")

def log_info(msg):
    _log_to_file(msg, "INFO")
    print(f"\033[96m[INFO] {msg}\033[0m")

def log_ok(msg):
    _log_to_file(msg, "OK")
    print(f"\033[92m[OK] {msg}\033[0m")

def log_error(msg):
    _log_to_file(msg, "ERROR")
    print(f"\033[91m[ERROR] {msg}\033[0m")

# --- Обработчики команд ---

def handle_status(args):
    fsm_client = FSMClient()
    fsm_state = fsm_client.get_state()
    mission_state = read_json_file(MISSION_STATUS_FILE)
    telemetry = read_json_file(TELEMETRY_FILE)
    health_report = read_json_file(os.path.join(project_root, 'logs', 'health_report.log'))
    consistency_log = read_json_file(os.path.join(project_root, 'logs', 'consistency_log.json'), default_val=[])

    fsm_state_label = loc.get_dual("FSM State", "Состояние FSM")
    log_info(f"{fsm_state_label}: {fsm_state.get('mode', 'N/A').upper()}")
    last_mission_label = loc.get_dual("Last Mission", "Последняя миссия")
    log_info(f"{last_mission_label}: {mission_state.get('current_mission', 'N/A')}")
    last_activity_label = loc.get_dual("Last Activity (Telemetry)", "Последняя активность (телеметрия)")
    log_info(f"{last_activity_label}: {telemetry.get('timestamp', 'N/A')}")

    errors_warnings = []
    if isinstance(consistency_log, list):
        for entry in consistency_log:
            if entry.get('level') in ['ERROR', 'WARNING']:
                errors_warnings.append(f"{entry.get('level')}: {entry.get('message')}")
    
    # Check for errors/warnings in the latest health report entry
    if health_report and isinstance(health_report, dict):
        latest_report_key = list(health_report.keys())[-1] # Get the latest timestamp key
        latest_report = health_report[latest_report_key]
        for component, status in latest_report.items():
            if status != "OK" and component != "agent_status": # Agent status handled separately
                errors_warnings.append(f"{component}: {status}")

    if errors_warnings:
        errors_warnings_label = loc.get_dual("Errors/Warnings Detected", "Обнаружены ошибки/предупреждения")
        log_info(f"{errors_warnings_label}:")
        for msg in errors_warnings:
            log_error(f"  - {msg}")
    else:
        no_errors_warnings_label = loc.get_dual("No Errors/Warnings Detected", "Ошибок/предупреждений не обнаружено")
        log_ok(no_errors_warnings_label)

def handle_agents(args):
    shared_bus_data = SharedBusManager().get_bus_data()
    if not shared_bus_data or "agents" not in shared_bus_data or not isinstance(shared_bus_data["agents"], dict):
        no_agent_data_label = loc.get_dual("No agent data found in shared_bus.json.", "Данные об агентах в shared_bus.json не найдены.")
        log_info(no_agent_data_label)
        return

    agent_status_label = loc.get_dual("Agent Status:", "Статус агентов:")
    log_info(agent_status_label)
    for agent_id, agent_info in shared_bus_data["agents"].items():
        last_heartbeat_str = agent_info.get("last_heartbeat")
        status_emoji = ""
        status_text = ""
        last_seen_str = loc.get_dual("Never", "Никогда")

        if last_heartbeat_str:
            try:
                # Handle both 'Z' and non-'Z' ISO formats
                if last_heartbeat_str.endswith('Z'):
                    last_heartbeat_time = datetime.fromisoformat(last_heartbeat_str[:-1])
                else:
                    last_heartbeat_time = datetime.fromisoformat(last_heartbeat_str)
                
                time_diff = datetime.utcnow() - last_heartbeat_time
                seconds_ago = int(time_diff.total_seconds())
                last_seen_str = loc.get_dual(f"{seconds_ago} seconds ago", f"{seconds_ago} секунд назад")

                if seconds_ago < 3:
                    status_emoji = "✅"
                    status_text = loc.get_dual("ALIVE", "АКТИВЕН")
                elif seconds_ago < 10:
                    status_emoji = "❌"
                    status_text = loc.get_dual("STALE", "УСТАРЕЛ")
                else:
                    status_emoji = "⛔️"
                    status_text = loc.get_dual("DEAD", "МЁРТВ")
            except ValueError:
                status_emoji = "❓"
                status_text = loc.get_dual("UNKNOWN (Invalid Heartbeat)", "НЕИЗВЕСТНО (Неверный формат Heartbeat)")
        else:
            status_emoji = "❓"
            status_text = loc.get_dual("UNKNOWN (No Heartbeat Data)", "НЕИЗВЕСТНО (Нет данных Heartbeat)")
        
        log_info(f"  {status_emoji} {agent_id} -> {status_text} (last seen: {last_seen_str})")

def handle_diagnostics(args):
    health_report = read_json_file(os.path.join(project_root, 'logs', 'health_report.log'))
    consistency_log = read_json_file(os.path.join(project_root, 'logs', 'consistency_log.json'), default_val=[])

    system_health_report_label = loc.get_dual("System Health Report:", "Отчет о состоянии системы:")
    log_info(system_health_report_label)
    if health_report and isinstance(health_report, dict):
        # Get the latest entry from the health report
        latest_timestamp = sorted(health_report.keys())[-1] if health_report else None
        if latest_timestamp:
            report = health_report[latest_timestamp]
            for key, value in report.items():
                if key == "agent_status":
                    agent_status_label = loc.get_dual("  Agent Status:", "  Статус агентов:")
                    log_info(agent_status_label)
                    for agent_id, status in value.items():
                        log_info(f"    - {agent_id}: {status}")
                else:
                    log_info(f"  {key}: {value}")
        else:
            no_recent_health_report_label = loc.get_dual("  No recent health report available.", "  Нет свежих отчетов о состоянии.")
        log_info(no_recent_health_report_label)
    else:
        health_report_not_found_label = loc.get_dual("  Health report file not found or empty.", "  Файл отчета о состоянии не найден или пуст.")
        log_info(health_report_not_found_label)

    consistency_check_log_label = loc.get_dual("Consistency Check Log:", "Журнал проверки согласованности:")
    log_info(consistency_check_log_label)
    if consistency_log and isinstance(consistency_log, list):
        if consistency_log:
            for entry in consistency_log:
                level = entry.get('level', 'INFO')
                message = entry.get('message', 'N/A')
                timestamp = entry.get('timestamp', 'N/A')
                log_info(f"  [{timestamp}] [{level}] {message}")
        else:
            no_consistency_issues_label = loc.get_dual("  No consistency issues logged.", "  Проблемы согласованности не зарегистрированы.")
            log_info(no_consistency_issues_label)
    else:
        consistency_log_not_found_label = loc.get_dual("  Consistency log file not found or empty.", "  Файл журнала согласованности не найден или пуст.")
        log_info(consistency_log_not_found_label)

    # Basic FSM vs Sensors vs Mission consistency check (as per prompt)
    fsm_client = FSMClient()
    fsm_state = fsm_client.get_state()
    sensors = read_json_file(os.path.join(project_root, 'sensors.json')) # Assuming sensors.json is in project root
    mission_state = read_json_file(MISSION_STATUS_FILE)

    fsm_sensors_mission_consistency_label = loc.get_dual("FSM-Sensors-Mission Consistency:", "Согласованность FSM-Сенсоры-Миссии:")
    log_info(fsm_sensors_mission_consistency_label)
    fsm_mode = fsm_state.get("mode", "UNKNOWN")
    mission_status = mission_state.get("status", "UNKNOWN")

    if fsm_mode == "MISSION_ACTIVE" and mission_status != "active":
        log_error(loc.get_dual("  FSM is MISSION_ACTIVE but mission status is not active.", "  FSM в состоянии MISSION_ACTIVE, но статус миссии не активен."))
    elif fsm_mode != "MISSION_ACTIVE" and mission_status == "active":
        log_error(loc.get_dual("  FSM is not MISSION_ACTIVE but mission status is active.", "  FSM не в состоянии MISSION_ACTIVE, но статус миссии активен."))
    else:
        log_ok(loc.get_dual("  FSM and Mission status are consistent.", "  Статус FSM и Миссии согласованы."))

    # Add more specific consistency checks here if needed, e.g., FSM state vs. specific sensor values
    # For example, if FSM is 'CHARGING', check if battery_percent is increasing
    # This would require more complex logic and access to historical sensor data.

def handle_agents(args):
    shared_bus_data = SharedBusManager().get_bus_data()
    if not shared_bus_data or "agents" not in shared_bus_data or not isinstance(shared_bus_data["agents"], dict):
        no_agent_data_label = loc.get_dual("No agent data found in shared_bus.json.", "Данные об агентах в shared_bus.json не найдены.")
        log_info(no_agent_data_label)
        return

    agent_status_label = loc.get_dual("Agent Status:", "Статус агентов:")
    log_info(agent_status_label)
    for agent_id, agent_info in shared_bus_data["agents"].items():
        last_heartbeat_str = agent_info.get("last_heartbeat")
        status_emoji = ""
        status_text = ""
        last_seen_str = loc.get_dual("Never", "Никогда")

        if last_heartbeat_str:
            try:
                # Handle both 'Z' and non-'Z' ISO formats
                if last_heartbeat_str.endswith('Z'):
                    last_heartbeat_time = datetime.fromisoformat(last_heartbeat_str[:-1])
                else:
                    last_heartbeat_time = datetime.fromisoformat(last_heartbeat_str)
                
                time_diff = datetime.utcnow() - last_heartbeat_time
                seconds_ago = int(time_diff.total_seconds())
                last_seen_str = loc.get_dual(f"{seconds_ago} seconds ago", f"{seconds_ago} секунд назад")

                if seconds_ago < 3:
                    status_emoji = "✅"
                    status_text = loc.get_dual("ALIVE", "АКТИВЕН")
                elif seconds_ago < 10:
                    status_emoji = "❌"
                    status_text = loc.get_dual("STALE", "УСТАРЕЛ")
                else:
                    status_emoji = "⛔️"
                    status_text = loc.get_dual("DEAD", "МЁРТВ")
            except ValueError:
                status_emoji = "❓"
                status_text = loc.get_dual("UNKNOWN (Invalid Heartbeat)", "НЕИЗВЕСТНО (Неверный формат Heartbeat)")
        else:
            status_emoji = "❓"
            status_text = loc.get_dual("UNKNOWN (No Heartbeat Data)", "НЕИЗВЕСТНО (Нет данных Heartbeat)")
        
        log_info(f"  {status_emoji} {agent_id} -> {status_text} (last seen: {last_seen_str})")

def handle_diagnostics(args):
    health_report = read_json_file(os.path.join(project_root, 'logs', 'health_report.log'))
    consistency_log = read_json_file(os.path.join(project_root, 'logs', 'consistency_log.json'), default_val=[])

    system_health_report_label = loc.get_dual("System Health Report:", "Отчет о состоянии системы:")
    log_info(system_health_report_label)
    if health_report and isinstance(health_report, dict):
        # Get the latest entry from the health report
        latest_timestamp = sorted(health_report.keys())[-1] if health_report else None
        if latest_timestamp:
            report = health_report[latest_timestamp]
            for key, value in report.items():
                if key == "agent_status":
                    agent_status_label = loc.get_dual("  Agent Status:", "  Статус агентов:")
                    log_info(agent_status_label)
                    for agent_id, status in value.items():
                        log_info(f"    - {agent_id}: {status}")
                else:
                    log_info(f"  {key}: {value}")
        else:
            no_recent_health_report_label = loc.get_dual("  No recent health report available.", "  Нет свежих отчетов о состоянии.")
        log_info(no_recent_health_report_label)
    else:
        health_report_not_found_label = loc.get_dual("  Health report file not found or empty.", "  Файл отчета о состоянии не найден или пуст.")
        log_info(health_report_not_found_label)

    consistency_check_log_label = loc.get_dual("Consistency Check Log:", "Журнал проверки согласованности:")
    log_info(consistency_check_log_label)
    if consistency_log and isinstance(consistency_log, list):
        if consistency_log:
            for entry in consistency_log:
                level = entry.get('level', 'INFO')
                message = entry.get('message', 'N/A')
                timestamp = entry.get('timestamp', 'N/A')
                log_info(f"  [{timestamp}] [{level}] {message}")
        else:
            no_consistency_issues_label = loc.get_dual("  No consistency issues logged.", "  Проблемы согласованности не зарегистрированы.")
            log_info(no_consistency_issues_label)
    else:
        consistency_log_not_found_label = loc.get_dual("  Consistency log file not found or empty.", "  Файл журнала согласованности не найден или пуст.")
        log_info(consistency_log_not_found_label)

    # Basic FSM vs Sensors vs Mission consistency check (as per prompt)
    fsm_client = FSMClient()
    fsm_state = fsm_client.get_state()
    sensors = read_json_file(os.path.join(project_root, 'sensors.json')) # Assuming sensors.json is in project root
    mission_state = read_json_file(MISSION_STATUS_FILE)

    fsm_sensors_mission_consistency_label = loc.get_dual("FSM-Sensors-Mission Consistency:", "Согласованность FSM-Сенсоры-Миссии:")
    log_info(fsm_sensors_mission_consistency_label)
    fsm_mode = fsm_state.get("mode", "UNKNOWN")
    mission_status = mission_state.get("status", "UNKNOWN")

    if fsm_mode == "MISSION_ACTIVE" and mission_status != "active":
        log_error(loc.get_dual("  FSM is MISSION_ACTIVE but mission status is not active.", "  FSM в состоянии MISSION_ACTIVE, но статус миссии не активен."))
    elif fsm_mode != "MISSION_ACTIVE" and mission_status == "active":
        log_error(loc.get_dual("  FSM is not MISSION_ACTIVE but mission status is active.", "  FSM не в состоянии MISSION_ACTIVE, но статус миссии активен."))
    else:
        log_ok(loc.get_dual("  FSM and Mission status are consistent.", "  Статус FSM и Миссии согласованы."))

    # Add more specific consistency checks here if needed, e.g., FSM state vs. specific sensor values
    # For example, if FSM is 'CHARGING', check if battery_percent is increasing
    # This would require more complex logic and access to historical sensor data.

def handle_move(args):
    if len(args) != 2:
        log_error("move требует 2 аргумента: x y")
        return
    try:
        x, y = float(args[0]), float(args[1])
        enqueue_event("MOVE_TO", "operator_cli", {"x": x, "y": y})
    except ValueError:
        log_error("Координаты должны быть числами.")

def handle_rotate(args):
    if len(args) != 1:
        log_error("rotate требует 1 аргумент: angle")
        return
    try:
        angle = float(args[0])
        enqueue_event("ROTATE_TO", "operator_cli", {"angle": angle})
    except ValueError:
        log_error("Угол должен быть числом.")

def handle_help(args):
    log_info(loc.get_dual("Available commands:", "Доступные команды:"))
    log_info(loc.get_dual("  status - show current system status", "  status - показать текущее состояние системы"))
    log_info(loc.get_dual("  agents - list all agents and their heartbeat status", "  agents - вывести список всех агентов и их статус heartbeat"))
    log_info(loc.get_dual("  diagnostics - run system diagnostics and consistency checks", "  diagnostics - запустить системную диагностику и проверку согласованности"))
    log_info(loc.get_dual("  move x y - move to coordinates", "  move x y - переместиться в координаты"))
    log_info(loc.get_dual("  rotate angle - rotate by angle", "  rotate angle - повернуться на угол"))
    log_info(loc.get_dual("  clear - clear screen", "  clear - очистить экран"))
    log_info(loc.get_dual("  exit - exit interface", "  exit - выйти из интерфейса"))

COMMAND_HANDLERS = {
    'status': handle_status,
    'agents': handle_agents,
    'diagnostics': handle_diagnostics,
    'move': handle_move,
    'rotate': handle_rotate,
    'help': handle_help,
}

# --- Главный цикл REPL ---

def run_command(command_line: str):
    parts = shlex.split(command_line)
    command = parts[0].lower()
    args = parts[1:]

    if command == 'clear':
        os.system('cls' if os.name == 'nt' else 'clear')
    elif command in COMMAND_HANDLERS:
        COMMAND_HANDLERS[command](args)
    else:
        unknown_command_label = loc.get_dual(f"Unknown command: {command}", f"Неизвестная команда: {command}")
        log_error(unknown_command_label)

def main(test_mode=False):
    if not test_mode:
        log_ok(loc.get_dual("QIKI Operator CLI started. Type 'help' for commands.", "QIKI Operator CLI запущен. Введите 'help' для списка команд."))
        while True:
            try:
                prompt = "QIKI> "
                cmd_input = input(prompt)
                if not cmd_input: continue

                if cmd_input.lower() == 'exit':
                    log_ok(loc.get_dual("Exiting CLI.", "Завершение работы CLI."))
                    break
                else:
                    run_command(cmd_input)

            except KeyboardInterrupt:
                log_ok(loc.get_dual("Exiting CLI.", "Завершение работы CLI."))
                break
            except Exception as e:
                log_error(loc.get_dual(f"An error occurred: {e}", f"Произошла ошибка: {e}"))
    else:
        # Test commands for programmatic execution
        test_commands = [
            "status",
            "agents",
            "diagnostics",
            "move 10 20",
            "rotate 90",
            "help",
            "unknown_command"
        ]
        for cmd in test_commands:
            log_info(f"--- Executing test command: {cmd} ---")
            run_command(cmd)
            time.sleep(0.1) # Small delay to ensure logs are written

    log_ok(loc.get_dual("CLI session ended.", "Сессия CLI завершена."))

if __name__ == "__main__":
    # Clear the log file before running tests
    if os.path.exists(CLI_INPUT_LOG_FILE):
        with open(CLI_INPUT_LOG_FILE, 'w') as f:
            f.truncate(0)
    
    # Run in test mode
    main(test_mode=True)
