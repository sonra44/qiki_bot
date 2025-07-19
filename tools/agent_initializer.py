import json
import os
from core.file_paths import FSM_STATE_FILE, TELEMETRY_FILE, SENSORS_FILE, FSM_REQUESTS_FILE
from core.agent_profile import AgentProfileManager

def initialize_json_file(file_path, default_content, overwrite=False):
    """Creates or overwrites a JSON file with default content."""
    if not os.path.exists(file_path) or overwrite:
        try:
            with open(file_path, 'w') as f:
                json.dump(default_content, f, indent=2)
            # print(f"Successfully initialized {file_path}")
        except IOError as e:
            print(f"Error initializing {file_path}: {e}")

def main():
    """Initializes all necessary data files and agents."""
    print("--- Running Agent and Data Initializer ---")

    # 1. Initialize core data files
    initialize_json_file(FSM_STATE_FILE, {"state": "idle"}, overwrite=True)
    initialize_json_file(TELEMETRY_FILE, {"battery_percent": 100.0, "speed_mps": 0.0, "power_wh": 100.0, "acceleration": 0.0}, overwrite=True)
    initialize_json_file(SENSORS_FILE, {"navigation": {"star_tracker": {"status": "OK", "tracking": false}, "gyroscope": {"angular_vel_x": 0.0, "angular_vel_y": 0.0, "angular_vel_z": 0.0}, "imu": {"accel_x": 0.0, "accel_y": 0.0, "accel_z": 0.0, "orientation_q": [1.0, 0.0, 0.0, 0.0]}}, "power": {"battery_main": {"voltage": 0.0, "current": 0.0, "temperature": 0.0, "soc": 100.0}, "solar_panels": {"voltage": 0.0, "current": 0.0, "charging": false}, "power_bus": {"voltage": 0.0, "load_current": 0.0}}, "thermal": {"core_temp": {"cpu": 0.0, "gpu": 0.0}, "radiators": {"panel_1_temp": 0.0}, "heat_pipes": {"flow_rate": 0.0, "pressure": 0.0}}, "communication": {"signal_strength_meters": {"rssi": -100.0, "snr": 0.0}, "antenna": {"azimuth": 0.0, "elevation": 0.0, "tracking": false}, "data_link": {"ber": 0.0, "throughput": 0.0}}, "structural": {"strain_gauges": {"hull_main": 0.0}, "vibration": {"x": 0.0, "y": 0.0, "z": 0.0}, "hull_pressure": {"internal": 0.0, "external": 0.0}}, "rlsm": {"radar": {"target_detected": false, "distance": 0.0}, "lidar": {"point_cloud_density": 0.0, "objects_detected": 0}, "spectrometer": {"composition": "N/A", "signal_strength": 0.0}, "magnetometer": {"field_strength": 0.0, "vector": [0.0, 0.0, 0.0]}}, "proximity": {"docking_sensors": {"front_distance": 999.0, "rear_distance": 999.0}, "collision_avoidance": {"min_distance": 999.0, "collision_imminent": false}, "range_finders": {"target_distance": 999.0, "target_locked": false}}, "thrusters": {"thrusters": {"main_thrust": 0.0, "fuel_flow": 0.0, "temp": 0.0}, "gimbal": {"pitch": 0.0, "yaw": 0.0}}, "environment": {"radiation_detector": {"level": 0.0, "alarm": false}, "micrometeorite_detector": {"impacts": 0, "last_impact_energy": 0.0}, "plasma_density": 0.0}, "system_health": {"data_bus": {"load": 0.0, "errors_per_min": 0}, "processor": {"load": 0.0, "core_voltage": 0.0}, "memory": {"ram_usage": 0.0, "ecc_errors": 0}}, "ew": {"jamming_detector": {"jamming_detected": false, "jamming_frequency": 0.0}, "signal_interceptor": {"signals_intercepted": 0, "strongest_signal": "N/A"}, "emcon_monitor": {"em_signature_level": 0.0}}}, overwrite=True)
    initialize_json_file(FSM_REQUESTS_FILE, [], overwrite=True) # Always clear the request queue
    # shared_bus.json is handled by AgentProfileManager implicitly

    # 2. Initialize agents
    manager = AgentProfileManager()

    agent_1 = {"id": "agent_001", "name": "Agent One", "state": "idle"}
    agent_2 = {"id": "agent_002", "name": "Agent Two", "state": "active"}

    manager.update(agent_1['id'], **agent_1)
    manager.update(agent_2['id'], **agent_2)

    print("--- Initialization Complete ---")

if __name__ == "__main__":
    main()