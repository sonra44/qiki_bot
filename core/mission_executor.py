import json
import os
import time
import datetime

# Add project root to sys.path for imports
import sys
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

from core.fsm_client import send_event
from core.telemetry import TelemetryManager
from core.sensors import SensorManager
from core.file_paths import MISSION_FILE

# --- Banner ---
def banner(title: str, description: str):
    print("=" * 80)
    print(f"  МОДУЛЬ: {title}")
    print(f"  Назначение: {description}")
    print(f"  Время запуска: {datetime.datetime.now().isoformat()}")
    print(f"  PID процесса: {os.getpid()}")
    print(f"  Путь: {os.path.abspath(__file__)}")
    print("=" * 80)
    print()

# --- End Banner ---

class MissionExecutor:
    def __init__(self):
        self.telemetry_manager = TelemetryManager()
        self.sensor_manager = SensorManager()
        self.mission = self._load_mission()
        print("[Mission Executor] Initialized.")

    def _load_mission(self):
        if not os.path.exists(MISSION_FILE):
            print(f"[Mission Executor] CRITICAL: Mission file not found at {MISSION_FILE}")
            return None
        try:
            with open(MISSION_FILE, 'r') as f:
                mission_data = json.load(f)
                print(f"[Mission Executor] Successfully loaded mission: {mission_data.get('mission_id')}")
                return mission_data
        except (json.JSONDecodeError, FileNotFoundError) as e:
            print(f"[Mission Executor] CRITICAL: Could not load or parse mission file: {e}")
            return None

    def _get_value_from_path(self, data: dict, path: str):
        parts = path.split('.')
        current_data = data
        for part in parts:
            if isinstance(current_data, dict) and part in current_data:
                current_data = current_data[part]
            else:
                return None
        return current_data

    def _evaluate_condition(self, condition_str: str, data_context: dict) -> bool:
        operators = {'>': lambda a, b: a > b, '<': lambda a, b: a < b, '==': lambda a, b: a == b,
                     '!=': lambda a, b: a != b, '>=': lambda a, b: a >= b, '<=': lambda a, b: a <= b}
        for op_str in sorted(operators.keys(), key=len, reverse=True):
            if op_str in condition_str:
                parts = condition_str.split(op_str, 1)
                field_path, value_str = parts[0].strip(), parts[1].strip()
                actual_value = self._get_value_from_path(data_context, field_path)
                if actual_value is None: return False
                try:
                    target_value = type(actual_value)(value_str)
                    return operators[op_str](actual_value, target_value)
                except (ValueError, TypeError):
                    return False
        return False

    def run_mission(self):
        if not self.mission or "steps" not in self.mission:
            print("[Mission Executor] No valid mission to run. Exiting.")
            return

        print(f"--- Starting Mission: {self.mission['description']} ---")

        for step in self.mission["steps"]:
            step_id = step.get("step_id", "N/A")
            action_desc = step.get("action", "No description")
            print(f"\n[STEP] ID: {step_id} - {action_desc}")

            # 1. Check condition
            if "condition" in step:
                telemetry_data = self.telemetry_manager.get()
                sensor_data = self.sensor_manager.get()
                data_context = {"telemetry": telemetry_data, "sensors": sensor_data}
                
                if not self._evaluate_condition(step["condition"], data_context):
                    print(f"[STEP] Condition '{step['condition']}' is FALSE. Skipping step.")
                    continue
                print(f"[STEP] Condition '{step['condition']}' is TRUE. Proceeding.")

            # 2. Send trigger
            if "trigger" in step:
                event = step["trigger"]
                print(f"[STEP] Sending trigger event '{event}' to FSM Gatekeeper.")
                send_event(event=event, source="mission_executor")

            # 3. Wait
            if "wait_seconds" in step:
                wait_time = step["wait_seconds"]
                print(f"[STEP] Waiting for {wait_time} seconds...")
                time.sleep(wait_time)

            # 4. Break
            if step.get("break", False):
                print("[Mission Executor] Break command received. Mission terminated.")
                break
        
        print("--- Mission Complete ---")

if __name__ == "__main__":
    banner(
        title="Mission Executor / Исполнитель Миссий",
        description="Загружает и выполняет пошаговые стратегические миссии."
    )
    executor = MissionExecutor()
    executor.run_mission()
