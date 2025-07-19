from core.sensors import SensorManager
import os
from core.file_paths import SENSORS_FILE
import json
import time

# Clean up old sensors.json for a fresh start for the test
if os.path.exists(SENSORS_FILE):
    os.remove(SENSORS_FILE)
    print(f"Cleaned up existing {SENSORS_FILE} for test.")

manager = SensorManager()

print("\n--- Testing SensorManager with simulated external updates ---")

# Simulate sensor_bus.py running and updating sensors.json
# This is a simplified simulation for testing purposes

def simulate_external_sensor_update(iteration):
    sample_data = {
        "navigation": {"star_tracker": {"is_locked": True, "tracking_stars": 15 + iteration}},
        "power": {"battery_main": {"soc": 75.5 - iteration * 5, "voltage": 12.1}},
        "rlsm": {"radar": {"target_detected": iteration % 2 == 0, "range": 100 * iteration}}
    }
    with open(SENSORS_FILE, 'w') as f:
        json.dump(sample_data, f, indent=2)
    print(f"[SIMULATION] Wrote simulated data to {SENSORS_FILE} (Iteration {iteration})")

for i in range(3):
    simulate_external_sensor_update(i)
    time.sleep(0.5) # Give a moment for file system to settle
    current_sensor_data = manager.get()
    print(f"[TEST] Sensor data from manager.get() (Iteration {i}):")
    print(json.dumps(current_sensor_data, indent=2))
    print("\n")

print("--- SensorManager Test Complete ---")
