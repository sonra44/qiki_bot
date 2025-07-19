import random
from .base_cluster import BaseSensorCluster

class NavigationCluster(BaseSensorCluster):
    def __init__(self):
        super().__init__(cluster_name="Navigation")
        # Initialize the data structure for this cluster
        self.data.update({
            "star_tracker": {"is_locked": False, "tracking_stars": 0},
            "gyroscope": {"pitch_rate": 0.0, "yaw_rate": 0.0, "roll_rate": 0.0},
            "imu": {"accel_x": 0.0, "accel_y": 0.0, "accel_z": 0.0, "orientation_q": [1, 0, 0, 0]}
        })

    def update(self):
        # Simulate Star Tracker
        is_locked = random.random() > 0.1 # 90% chance to be locked
        self.data["star_tracker"]["is_locked"] = is_locked
        self.data["star_tracker"]["tracking_stars"] = random.randint(5, 50) if is_locked else 0

        # Simulate Gyroscope
        self.data["gyroscope"]["pitch_rate"] = self._generate_value(0, 0.05)
        self.data["gyroscope"]["yaw_rate"] = self._generate_value(0, 0.05)
        self.data["gyroscope"]["roll_rate"] = self._generate_value(0, 0.05)

        # Simulate IMU
        self.data["imu"]["accel_x"] = self._generate_value(0, 0.1)
        self.data["imu"]["accel_y"] = self._generate_value(0, 0.1)
        self.data["imu"]["accel_z"] = self._generate_value(-9.8, 0.1) # Simulate gravity

    def validate(self):
        super().validate() # Perform base validation
        # Custom validation for Navigation cluster
        if not self.data["star_tracker"]["is_locked"]:
            self.data["status"] = "WARNING"
            self.data["errors"].append("Star tracker is not locked.")
        
        # Example: Check if IMU is providing near-zero acceleration when idle
        idle_accel_threshold = 1.0
        accel_magnitude = (
            self.data["imu"]["accel_x"]**2 + 
            self.data["imu"]["accel_y"]**2 + 
            (self.data["imu"]["accel_z"] + 9.8)**2
        )**0.5
        
        if accel_magnitude > idle_accel_threshold:
            self.data["status"] = "WARNING"
            self.data["errors"].append(f"IMU acceleration ({accel_magnitude:.2f}) exceeds idle threshold.")
