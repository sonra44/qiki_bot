import json
import os
import subprocess
import time
import argparse
import shutil

# --- Константы ---
QIKI_BOT_DIR = '/data/data/com.termux/files/home/qiki_bot'
FSM_REQUESTS_FILE = os.path.join(QIKI_BOT_DIR, 'fsm_requests.json')
CLI_PATH = os.path.join(QIKI_BOT_DIR, 'operator_interface.py')

# --- Утилиты ---
def log_info(msg): print(f"\u001b[96m[INFO] {msg}\u001b[0m")
def log_ok(msg): print(f"\u001b[92m[OK] {msg}\u001b[0m")
def log_error(msg): print(f"\u001b[91m[FAIL] {msg}\u001b[0m")
def log_warn(msg): print(f"\u001b[93m[WARN] {msg}\u001b[0m")

def read_json_file(file_path, default_val={}):
    if not os.path.exists(file_path) or os.path.getsize(file_path) == 0:
        return default_val
    try:
        with open(file_path, 'r') as f: return json.load(f)
    except (json.JSONDecodeError, IOError): return default_val

# --- Основная логика тестера ---

def check_expectation(expectation):
    if not expectation: return True, "No expectation set."

    if 'fsm_requests.command' in expectation:
        requests = read_json_file(FSM_REQUESTS_FILE, [])
        if not requests: return False, "fsm_requests.json is empty."
        last_request = requests[-1]
        if last_request.get('command') != expectation['fsm_requests.command']:
            return False, f"Expected command {expectation['fsm_requests.command']}, got {last_request.get('command')}"
        if 'fsm_requests.payload' in expectation:
            if last_request.get('payload') != expectation['fsm_requests.payload']:
                return False, f"Payload mismatch."
    return True, "Expectation met."

def run_scenario(scenario_path, debug=False):
    log_info(f"Запуск сценария: {scenario_path}")
    
    try:
        with open(scenario_path, 'r') as f: scenario = json.load(f)
    except (IOError, json.JSONDecodeError) as e:
        log_error(f"Не удалось прочитать или разобрать файл сценария: {e}")
        return False

    # Backup and clear requests file
    requests_backup_path = FSM_REQUESTS_FILE + ".bak"
    if os.path.exists(FSM_REQUESTS_FILE):
        shutil.copy(FSM_REQUESTS_FILE, requests_backup_path)
    with open(FSM_REQUESTS_FILE, 'w') as f: json.dump([], f)

    cli_process = subprocess.Popen(
        ['python3', CLI_PATH],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1
    )

    time.sleep(1) # Даем CLI время на инициализацию

    passed_steps = 0
    total_steps = len(scenario)

    for i, step in enumerate(scenario):
        log_info(f"--- Шаг {i+1}/{total_steps}: Ввод '{step['input']}' ---")
        cli_process.stdin.write(step['input'] + '\n')
        cli_process.stdin.flush()
        
        if 'wait' in step:
            time.sleep(step['wait'])

        success, message = check_expectation(step.get('expect'))
        if success:
            log_ok(f"Шаг пройден. {message}")
            passed_steps += 1
        else:
            log_error(f"Шаг провален. {message}")

    cli_process.stdin.write('exit\n')
    cli_process.stdin.flush()
    cli_process.terminate()
    cli_process.wait(timeout=2)

    # Restore requests file
    if os.path.exists(requests_backup_path):
        shutil.move(requests_backup_path, FSM_REQUESTS_FILE)

    log_info("--- Отчет ---")
    if passed_steps == total_steps:
        log_ok(f"Все {total_steps} шагов сценария '{os.path.basename(scenario_path)}' успешно пройдены!")
    else:
        log_error(f"Провалено {total_steps - passed_steps} из {total_steps} шагов.")
    
    return passed_steps == total_steps

def main():
    parser = argparse.ArgumentParser(description="CLI Scenario Tester for QIKI Bot")
    parser.add_argument('scenario_files', nargs='+', help='Пути к файлам сценариев (*.json)')
    parser.add_argument('--debug', action='store_true', help='Включить отладочный вывод')
    args = parser.parse_args()

    all_scenarios_passed = True
    for scenario_file in args.scenario_files:
        if not run_scenario(scenario_file, args.debug):
            all_scenarios_passed = False
    
    if not all_scenarios_passed:
        exit(1)

if __name__ == "__main__":
    main()
