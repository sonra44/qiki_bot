import json
import os
import time

# Add project root to sys.path for imports
import sys
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.append(project_root)

from core.telemetry import TelemetryManager
from core.sensors import SensorManager
from core.fsm import SimpleFSM
from core.file_paths import TELEMETRY_FILE, SENSORS_FILE, FSM_STATE_FILE, RULES_FILE
from core.file_paths import RULES_FILE

class RuleEngine:
    def __init__(self):
        self.fsm = SimpleFSM()
        self.telemetry_manager = TelemetryManager()
        self.sensor_manager = SensorManager()
        self.rules = self._load_rules()
        print("RuleEngine initialized.")

    def _load_rules(self) -> list:
        """Loads rules from rules.json or creates a default if not found/corrupt."""
        if not os.path.exists(RULES_FILE):
            print(f"Info: {RULES_FILE} not found. Creating with default rules.")
            default_rules = [
                {
                    "name": "LowBatteryCharge",
                    "condition": "telemetry.battery_percent < 20",
                    "action": "charge",
                    "priority": 10
                },
                {
                    "name": "BatteryCharged",
                    "condition": "telemetry.battery_percent > 95 and fsm.state == 'charging'",
                    "action": "idle", # Assuming 'stop_charge' leads to 'idle'
                    "priority": 20
                },
                {
                    "name": "StartMoving",
                    "condition": "fsm.state == 'idle' and telemetry.battery_percent > 30",
                    "action": "start_move",
                    "priority": 30
                },
                {
                    "name": "StuckDetection",
                    "condition": "fsm.state == 'moving' and telemetry.velocity == 0",
                    "action": "error",
                    "priority": 5
                },
                {
                    "name": "HighTemperature",
                    "condition": "sensors.thermal.core_temp.cpu > 80",
                    "action": "error",
                    "priority": 1
                },
                {
                    "name": "RecoverFromError",
                    "condition": "fsm.state == 'error' and telemetry.battery_percent > 10",
                    "action": "reset",
                    "priority": 0
                }
            ]
            os.makedirs(os.path.dirname(RULES_FILE), exist_ok=True)
            try:
                with open(RULES_FILE, 'w') as f:
                    json.dump(default_rules, f, indent=2)
                print(f"Info: Successfully created default {RULES_FILE}.")
            except IOError as e:
                print(f"Error: Could not write default {RULES_FILE}: {e}")
            return default_rules

        try:
            with open(RULES_FILE, 'r') as f:
                rules = json.load(f)
                print(f"Info: Successfully loaded rules from {RULES_FILE}.")
                # Sort rules by priority (lower number = higher priority)
                return sorted(rules, key=lambda x: x.get('priority', 999))
        except json.JSONDecodeError as e:
            print(f"Error: Corrupt JSON in {RULES_FILE}: {e}. Returning empty rules list.")
            return []
        except Exception as e:
            print(f"Error: Unexpected error reading {RULES_FILE}: {e}. Returning empty rules list.")
            return []

    def _get_value_from_path(self, data: dict, path: str):
        """Helper to get a nested value from a dictionary using dot notation."""
        parts = path.split('.')
        current_data = data
        for part in parts:
            if isinstance(current_data, dict) and part in current_data:
                current_data = current_data[part]
            else:
                return None # Path not found
        return current_data

    def _evaluate_single_condition(self, condition_str: str, data_context: dict) -> bool:
        """Safely evaluates a single comparison condition (e.g., 'field < value')."""
        # Supported operators
        operators = {'>': lambda a, b: a > b, '<': lambda a, b: a < b, '==': lambda a, b: a == b,
                     '!=': lambda a, b: a != b, '>=': lambda a, b: a >= b, '<=': lambda a, b: a <= b}

        # Find the operator in the string
        op = None
        for operator_str in sorted(operators.keys(), key=len, reverse=True): # Check longer ops first (e.g., >= before >)
            if operator_str in condition_str:
                parts = condition_str.split(operator_str, 1)
                if len(parts) == 2:
                    field_path = parts[0].strip()
                    value_str = parts[1].strip()
                    op = operator_str
                    break
        
        if not op:
            print(f"Warning: No valid operator found in condition: {condition_str}")
            return False

        actual_value = self._get_value_from_path(data_context, field_path)
        if actual_value is None:
            print(f"Warning: Field '{field_path}' not found in data context for condition '{condition_str}'.")
            return False

        # Attempt to convert value_str to appropriate type based on actual_value's type
        try:
            if isinstance(actual_value, (int, float)):
                target_value = float(value_str)
            elif isinstance(actual_value, bool):
                target_value = value_str.lower() == 'true'
            else: # Treat as string
                target_value = value_str.strip("'\"") # Remove quotes if present
        except ValueError:
            print(f"Warning: Type conversion failed for '{value_str}' in condition '{condition_str}'.")
            return False

        return operators[op](actual_value, target_value)

    def _evaluate_complex_condition(self, condition_str: str, data_context: dict) -> bool:
        """Evaluates complex conditions with 'and'/'or' operators."""
        # This is a simplified parser for 'and'/'or' and assumes no parentheses
        # For more complex logic, a proper expression parser would be needed.

        if " and " in condition_str:
            sub_conditions = condition_str.split(" and ")
            return all(self._evaluate_single_condition(sub.strip(), data_context) for sub in sub_conditions)
        elif " or " in condition_str:
            sub_conditions = condition_str.split(" or ")
            return any(self._evaluate_single_condition(sub.strip(), data_context) for sub in sub_conditions)
        else:
            return self._evaluate_single_condition(condition_str, data_context)

    def run_once(self) -> str | None:
        """Checks rules and returns the event of the first matching rule."""
        telemetry_data = self.telemetry_manager.get()
        sensor_data = self.sensor_manager.get()
        fsm_state = self.fsm.get_state()

        data_context = {
            "telemetry": telemetry_data,
            "sensors": sensor_data,
            "fsm": {"state": fsm_state}
        }

        for rule in self.rules:
            rule_name = rule.get('name', 'Unnamed Rule')
            condition_str = rule.get('condition')
            action = rule.get('action')

            if not condition_str or not action:
                continue

            try:
                if self._evaluate_complex_condition(condition_str, data_context):
                    print(f"[Rule Engine] Rule '{rule_name}' is TRUE. Proposing event '{action}'.")
                    return action # Return the event name
            except Exception as e:
                print(f"[Rule Engine] ERROR evaluating rule '{rule_name}': {e}")
        
        return None # No rule fired

    def run_loop(self, interval: int = 2):
        """Regularly applies rules in a loop."""
        print(f"RuleEngine: Starting rule evaluation loop (every {interval} seconds)...")
        while True:
            self.run_once()
            time.sleep(interval)

# Example usage
if __name__ == "__main__":
    print("--- RuleEngine Test ---")

    # Ensure necessary files exist for testing
    # (In a real scenario, other components would create/update these)
    if not os.path.exists(TELEMETRY_FILE):
        tm = TelemetryManager()
        tm.update({"battery_percent": 80.0, "velocity": 0.5})
    
    if not os.path.exists(SENSORS_FILE):
        sm = SensorManager()
        sm.update()
    
    if not os.path.exists(FSM_STATE_FILE):
        fsm = SimpleFSM()
        pass # FSM handles its own file creation

    engine = RuleEngine()
    
    # Manual test loop
    print("\nStarting manual rule evaluation. Press Ctrl+C to exit.")
    try:
        while True:
            engine.run_once()
            time.sleep(1) # Shorter sleep for manual testing
    except KeyboardInterrupt:
        print("\nRuleEngine test terminated.")