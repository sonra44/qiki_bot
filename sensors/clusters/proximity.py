import random
from .base_cluster import BaseSensorCluster

class ProximityCluster(BaseSensorCluster):
    def __init__(self):
        super().__init__(cluster_name="Proximity")
        self.data.update({
            "docking_sensors": {"front_distance": 999, "rear_distance": 999},
            "collision_avoidance": {"min_distance": 999, "collision_imminent": False},
            "range_finders": {"target_range": 0, "target_locked": False}
        })

    def update(self):
        # Simulate Docking Sensors
        self.data["docking_sensors"]["front_distance"] = self._generate_value(5, 2) if random.random() < 0.1 else 999
        self.data["docking_sensors"]["rear_distance"] = self._generate_value(5, 2) if random.random() < 0.05 else 999

        # Simulate Collision Avoidance
        min_dist = self._generate_value(50, 20) if random.random() < 0.2 else 999
        self.data["collision_avoidance"]["min_distance"] = min_dist
        self.data["collision_avoidance"]["collision_imminent"] = min_dist < 10

        # Simulate Range Finders
        target_locked = random.random() < 0.3
        self.data["range_finders"]["target_locked"] = target_locked
        self.data["range_finders"]["target_range"] = self._generate_value(200, 50) if target_locked else 0

    def validate(self):
        super().validate()
        if self.data["collision_avoidance"]["collision_imminent"]:
            self.data["status"] = "ERROR"
            self._add_error(f"Collision imminent! Minimum distance: {self.data['collision_avoidance']['min_distance']:.1f}m")
        elif self.data["collision_avoidance"]["min_distance"] < 50:
            self.data["status"] = "WARNING"
            self._add_error(f"Object in close proximity: {self.data['collision_avoidance']['min_distance']:.1f}m")
