import json
import os
from typing import Dict, Any
from core.file_paths import TELEMETRY_FILE
import datetime

def banner(title: str, description: str):
    print("=" * 80)
    print(f"  МОДУЛЬ: {title}")
    print(f"  Назначение: {description}")
    print(f"  Время запуска: {datetime.datetime.now().isoformat()}")
    print(f"  PID процесса: {os.getpid()}")
    print(f"  Путь: {os.path.abspath(__file__)}")
    print("=" * 80)
    print()

banner(
    title="Telemetry Manager / Менеджер Телеметрии",
    description="Управляет данными телеметрии QIKI Bot."
)

class TelemetryManager:
    DEFAULT_TELEMETRY: Dict[str, Any] = {
        "battery_percent": 100.0,
        "power_wh": 500.0,
        "speed_mps": 0.0,
        "consumption_w": 0.0,
        "velocity": 0.0,
        "acceleration": 0.0,
        "impulse_active": False
    }

    def __init__(self):
        self.telemetry_data: Dict[str, Any] = self._load_telemetry()
        print(f"TelemetryManager initialized. Current data: {self.telemetry_data}")

    def _load_telemetry(self) -> Dict[str, Any]:
        """Loads telemetry data from telemetry.json or initializes defaults."""
        if os.path.exists(TELEMETRY_FILE):
            try:
                with open(TELEMETRY_FILE, 'r') as f:
                    data = json.load(f)
                    print(f"Info: Successfully loaded telemetry from {TELEMETRY_FILE}.")
                    # Merge with defaults to ensure all keys are present and types are consistent
                    merged_data = self.DEFAULT_TELEMETRY.copy()
                    for key, default_value in self.DEFAULT_TELEMETRY.items():
                        if key in data:
                            # Attempt to cast to default type, or use default if type mismatch
                            try:
                                if isinstance(default_value, (int, float)):
                                    merged_data[key] = type(default_value)(data[key])
                                elif isinstance(default_value, bool):
                                    merged_data[key] = bool(data[key])
                                else:
                                    merged_data[key] = data[key]
                            except (ValueError, TypeError):
                                print(f"Warning: Type mismatch for key '{key}' in {TELEMETRY_FILE}. Using default value.")
                                merged_data[key] = default_value
                        else:
                            merged_data[key] = default_value
                    return merged_data
            except (json.JSONDecodeError, FileNotFoundError) as e:
                print(f"Warning: Could not read {TELEMETRY_FILE} or file is corrupt ({e}). Initializing with default values.")
                self._save_telemetry(self.DEFAULT_TELEMETRY) # Save defaults if file is bad
                return self.DEFAULT_TELEMETRY
        else:
            print(f"Info: {TELEMETRY_FILE} not found. Initializing with default values.")
            self._save_telemetry(self.DEFAULT_TELEMETRY) # Save initial defaults
            return self.DEFAULT_TELEMETRY

    def _save_telemetry(self, data_to_save: Dict[str, Any]):
        """Saves the given telemetry data to telemetry.json."""
        try:
            with open(TELEMETRY_FILE, 'w') as f:
                json.dump(data_to_save, f, indent=2)
            print(f"Info: Successfully saved telemetry to {TELEMETRY_FILE}.")
        except IOError as e:
            print(f"Error: Could not write to {TELEMETRY_FILE}: {e}")

    def get(self) -> Dict[str, Any]:
        """Returns the current telemetry data."""
        return self.telemetry_data

    def update(self, new_data: Dict[str, Any]):
        """Updates the telemetry data with new_data and saves it."""
        print(f"Info: Updating telemetry with: {new_data}")
        # Only update keys that are part of DEFAULT_TELEMETRY
        for key, value in new_data.items():
            if key in self.DEFAULT_TELEMETRY:
                # Attempt to cast to the expected type
                expected_type = type(self.DEFAULT_TELEMETRY[key])
                try:
                    self.telemetry_data[key] = expected_type(value)
                except (ValueError, TypeError):
                    print(f"Warning: Could not cast value '{value}' for key '{key}' to {expected_type}. Skipping update for this key.")
            else:
                print(f"Warning: Key '{key}' not in DEFAULT_TELEMETRY. Skipping update for this key.")
        self._save_telemetry(self.telemetry_data)

    def save(self):
        """Explicitly saves the current telemetry data to file."""
        print("Info: Explicitly saving current telemetry.")
        self._save_telemetry(self.telemetry_data)

# Example usage (for testing this module directly)
if __name__ == "__main__":
    print("--- TelemetryManager Test ---")

    # Clean up old telemetry.json for a fresh start
    if os.path.exists(TELEMETRY_FILE):
        os.remove(TELEMETRY_FILE)
        print(f"Cleaned up existing {TELEMETRY_FILE} for test.")

    # Test initialization with no file
    tm = TelemetryManager()
    print(f"Initial telemetry (should be default): {tm.get()}")

    # Test update
    tm.update({"battery_percent": 75.5, "speed_mps": 0.5, "new_field": "should_be_ignored"})
    print(f"Telemetry after update: {tm.get()}")

    # Test loading from existing file
    tm2 = TelemetryManager()
    print(f"Second manager initial telemetry (should be updated): {tm2.get()}")

    # Test explicit save
    tm2.telemetry_data["power_wh"] = 400.0 # Direct modification for testing save
    tm2.save()
    tm3 = TelemetryManager()
    print(f"Third manager initial telemetry (should reflect explicit save): {tm3.get()}")

    # Simulate corrupted file (optional, for manual testing)
    # with open(TELEMETRY_FILE, 'w') as f:
    #     f.write("invalid json")
    # tm_corrupt = TelemetryManager()
    # print(f"Telemetry after corrupt file: {tm_corrupt.get()}")

    print("--- TelemetryManager Test Complete ---")