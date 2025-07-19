import math
import datetime

class SensorPreprocessor:
    def __init__(self, raw_data: dict):
        print("[Preprocessor] Initializing SensorPreprocessor.")
        self.raw_data = raw_data
        self.processed_data = raw_data.copy() # Start with a copy of raw data
        self.validation_errors = []

    def filter_noise(self):
        print("[Preprocessor] Filtering noise from sensor data.")
        # Define acceptable ranges for specific sensors
        # Using None for out-of-range values as per prompt's optional suggestion

        # Navigation Cluster
        # Gyroscope (angular_vel_x/y/z) - assuming these are now part of NavigationCluster
        # The prompt mentions 'gyro.angular_vel_x/y/z' but the new structure is 'navigation.gyroscope.pitch_rate' etc.
        # I'll adapt to the new structure.
        if "navigation" in self.processed_data and "gyroscope" in self.processed_data["navigation"]:
            gyro = self.processed_data["navigation"]["gyroscope"]
            for key in ["pitch_rate", "yaw_rate", "roll_rate"]:
                if key in gyro and not (-500 <= gyro[key] <= 500):
                    print(f"[Preprocessor] Filtering: navigation.gyroscope.{key} out of range ({gyro[key]}). Setting to None.")
                    gyro[key] = None
        
        # Proximity Cluster
        # The prompt mentions 'proximity' as a top-level key, but it's now a cluster.
        # I'll assume it refers to 'proximity.collision_avoidance.min_distance' or similar.
        # For simplicity, I'll apply it to 'min_distance' in collision_avoidance.
        if "proximity" in self.processed_data and "collision_avoidance" in self.processed_data["proximity"]:
            min_dist = self.processed_data["proximity"]["collision_avoidance"].get("min_distance")
            if min_dist is not None and not (0.0 <= min_dist <= 10.0):
                print(f"[Preprocessor] Filtering: proximity.collision_avoidance.min_distance out of range ({min_dist}). Setting to None.")
                self.processed_data["proximity"]["collision_avoidance"]["min_distance"] = None

        # Thermal Cluster
        # thermo_cam - assuming this refers to core_temp in ThermalCluster
        if "thermal" in self.processed_data and "core_temp" in self.processed_data["thermal"]:
            core_temp = self.processed_data["thermal"]["core_temp"]
            for key in ["cpu", "gpu"]: # Assuming these are in Celsius
                if key in core_temp and not (-50 <= core_temp[key] <= 150):
                    print(f"[Preprocessor] Filtering: thermal.core_temp.{key} out of range ({core_temp[key]}). Setting to None.")
                    core_temp[key] = None

        # RLSM Cluster
        # magnetometer.field_strength
        if "rlsm" in self.processed_data and "magnetometer" in self.processed_data["rlsm"]:
            field_strength = self.processed_data["rlsm"]["magnetometer"].get("field_strength")
            if field_strength is not None and not (0 <= field_strength <= 1000):
                print(f"[Preprocessor] Filtering: rlsm.magnetometer.field_strength out of range ({field_strength}). Setting to None.")
                self.processed_data["rlsm"]["magnetometer"]["field_strength"] = None

    def normalize(self):
        print("[Preprocessor] Normalizing sensor data (placeholder - no specific normalization applied yet).")
        # This method can be extended later for specific normalization needs,
        # e.g., scaling values to a 0-1 range, converting units, etc.
        pass

    def validate(self):
        print("[Preprocessor] Validating sensor data structure and basic integrity.")
        self.validation_errors = []

        # Check for presence of key clusters
        expected_clusters = ["navigation", "power", "thermal", "structural", "system_health", "thrusters", "rlsm", "proximity", "environment", "communication", "ew"]
        for cluster_name in expected_clusters:
            if cluster_name not in self.processed_data:
                self.validation_errors.append(f"Missing expected cluster: {cluster_name}")
                print(f"[Preprocessor] Validation Error: Missing cluster '{cluster_name}'.")
            elif not isinstance(self.processed_data[cluster_name], dict):
                self.validation_errors.append(f"Cluster '{cluster_name}' is not a dictionary.")
                print(f"[Preprocessor] Validation Error: Cluster '{cluster_name}' is not a dictionary.")
            
            # Check for 'status' and 'errors' fields from BaseSensorCluster
            if cluster_name in self.processed_data:
                cluster_data = self.processed_data[cluster_name]
                if "status" not in cluster_data:
                    self.validation_errors.append(f"Cluster '{cluster_name}' is missing 'status' field.")
                    print(f"[Preprocessor] Validation Error: Cluster '{cluster_name}' missing 'status'.")
                if "errors" not in cluster_data:
                    self.validation_errors.append(f"Cluster '{cluster_name}' is missing 'errors' field.")
                    print(f"[Preprocessor] Validation Error: Cluster '{cluster_name}' missing 'errors'.")
                elif (cluster_data.get("status") == "ERROR" or cluster_data.get("status") == "WARNING") and cluster_data.get("errors"):
                    self.validation_errors.append(f"Cluster '{cluster_name}' reported errors: {cluster_data['errors']}")
                    print(f"[Preprocessor] Validation Error: Cluster '{cluster_name}' reported errors: {cluster_data['errors']}.")

        if not self.validation_errors:
            print("[Preprocessor] Data validation successful.")
        else:
            print(f"[Preprocessor] Data validation completed with {len(self.validation_errors)} errors.")

    def get_clean_data(self) -> dict:
        print("[Preprocessor] Returning cleaned sensor data.")
        return self.processed_data

def test():
    print("\n--- Running SensorPreprocessor Test ---")

    # Example raw data (simulating sensors.json output)
    raw_test_data = {
        "navigation": {
            "status": "OK",
            "errors": [],
            "gyroscope": {"pitch_rate": 10.5, "yaw_rate": -600.0, "roll_rate": 0.1}, # yaw_rate out of range
            "imu": {"accel_x": 0.0, "accel_y": 0.0, "accel_z": -9.8}
        },
        "power": {
            "status": "WARNING",
            "errors": ["Main battery SOC low: 15.0%"],
            "battery_main": {"voltage": 11.0, "soc": 15.0}
        },
        "thermal": {
            "status": "OK",
            "errors": [],
            "core_temp": {"cpu": 70.0, "gpu": 160.0} # gpu out of range
        },
        "proximity": {
            "status": "OK",
            "errors": [],
            "collision_avoidance": {"min_distance": 5.5}
        },
        "rlsm": {
            "status": "OK",
            "errors": [],
            "magnetometer": {"field_strength": 1200} # out of range
        },
        # Missing some clusters to test validation
        "communication": {
            "status": "OK",
            "errors": [],
            "signal_strength": {"rssi": -70.0}
        }
    }

    processor = SensorPreprocessor(raw_test_data)
    processor.filter_noise()
    processor.normalize()
    processor.validate()
    clean_data = processor.get_clean_data()

    print("\n[Preprocessor Test] Original Raw Data:")
    print(raw_test_data)
    print("\n[Preprocessor Test] Cleaned Data:")
    print(clean_data)
    print("\n[Preprocessor Test] Validation Errors:")
    if processor.validation_errors:
        for error in processor.validation_errors:
            print(f"- {error}")
    else:
        print("No validation errors.")

    # Assertions for automated check
    assert clean_data["navigation"]["gyroscope"]["yaw_rate"] is None, "Yaw rate should be None after filtering."
    assert clean_data["thermal"]["core_temp"]["gpu"] is None, "GPU temp should be None after filtering."
    assert clean_data["rlsm"]["magnetometer"]["field_strength"] is None, "Magnetometer field strength should be None after filtering."
    assert any("Missing expected cluster: structural" in err for err in processor.validation_errors), "Missing structural cluster should be reported."
    assert any("Cluster 'power' reported errors" in err for err in processor.validation_errors), "Power cluster errors should be reported."

    print("\n--- SensorPreprocessor Test Complete (Assertions Passed) ---")

if __name__ == "__main__":
    test()
