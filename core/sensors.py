import json
import os
import datetime
from typing import Dict, Any
from core.file_paths import SENSORS_FILE

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
    title="Sensor Manager / Менеджер Сенсоров",
    description="Предоставляет актуальные данные сенсоров QIKI Bot из sensors.json."
)

class SensorManager:
    def __init__(self):
        self.sensor_data: Dict[str, Any] = {}
        self._load_sensors()
        print(f"SensorManager initialized. Current data: {self.sensor_data}")

    def _load_sensors(self) -> None:
        """Loads sensor data from sensors.json or initializes an empty dict if not found/corrupt."""
        if os.path.exists(SENSORS_FILE):
            try:
                with open(SENSORS_FILE, 'r') as f:
                    content = f.read() # Read content first
                    if not content.strip(): # Check if content is empty
                        print(f"Warning: {SENSORS_FILE} is empty. Initializing with empty data.")
                        self.sensor_data = {}
                        self._save_sensors() # Save empty dict to ensure valid JSON
                        return
                    self.sensor_data = json.loads(content) # Load from content
                    print(f"Info: Successfully loaded sensor data from {SENSORS_FILE}.")
            except (json.JSONDecodeError, FileNotFoundError) as e:
                print(f"Warning: Could not read {SENSORS_FILE} or file is corrupt ({e}). Initializing with empty data.")
                self.sensor_data = {}
                self._save_sensors() # Save empty dict if file is bad
        else:
            print(f"Info: {SENSORS_FILE} not found. Initializing with empty data.")
            self.sensor_data = {}
            self._save_sensors() # Save initial empty dict

    def _save_sensors(self):
        """Saves the current sensor data to sensors.json. Used for initialization/recovery."""
        try:
            with open(SENSORS_FILE, 'w') as f:
                json.dump(self.sensor_data, f, indent=2)
            print(f"[INFO] {SENSORS_FILE} initialized/recovered successfully.")
        except Exception as e:
            print(f"[ERROR] Failed to save {SENSORS_FILE}: {e}")

    def get(self) -> Dict[str, Any]:
        """Returns the current sensor data, reloading it from file to ensure freshness."""
        self._load_sensors() # Reload to get the latest data from sensor_bus.py
        return self.sensor_data

# Main execution block for testing
if __name__ == "__main__":
    print("--- SensorManager Test ---")

    # Clean up old sensors.json for a fresh start
    if os.path.exists(SENSORS_FILE):
        os.remove(SENSORS_FILE)
        print(f"Cleaned up existing {SENSORS_FILE} for test.")

    manager = SensorManager()
    print(f"Initial sensor data (should be empty or default from bus): {manager.get()}")

    # In a real scenario, sensor_bus.py would be running and updating sensors.json
    # For this test, we'll simulate a simple update to sensors.json
    print("\nSimulating an external update to sensors.json...")
    sample_data = {
        "navigation": {"star_tracker": {"is_locked": True, "tracking_stars": 15}},
        "power": {"battery_main": {"soc": 75.5, "voltage": 12.1}}
    }
    with open(SENSORS_FILE, 'w') as f:
        json.dump(sample_data, f, indent=2)
    print("Simulated data written to sensors.json.")

    print(f"Sensor data after simulated external update: {manager.get()}")

    print("--- SensorManager Test Complete ---")
