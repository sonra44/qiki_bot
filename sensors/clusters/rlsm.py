import random
from .base_cluster import BaseSensorCluster

class RLSMCluster(BaseSensorCluster):
    def __init__(self):
        super().__init__(cluster_name="RLSM")
        self.data.update({
            "radar": {"target_detected": False, "range": 0, "azimuth": 0, "elevation": 0},
            "lidar": {"point_cloud_density": 0, "objects_detected": 0},
            "spectrometer": {"composition": {}, "signal_strength": 0},
            "magnetometer": {"field_strength": 0, "vector": [0, 0, 0]}
        })

    def update(self):
        # Simulate Radar
        target_detected = random.random() < 0.2 # 20% chance
        self.data["radar"]["target_detected"] = target_detected
        if target_detected:
            self.data["radar"]["range"] = self._generate_value(1000, 500)
            self.data["radar"]["azimuth"] = self._generate_value(0, 180)
            self.data["radar"]["elevation"] = self._generate_value(0, 90)
        else:
            self.data["radar"]["range"] = 0
            self.data["radar"]["azimuth"] = 0
            self.data["radar"]["elevation"] = 0

        # Simulate Lidar
        objects_detected = random.randint(0, 10)
        self.data["lidar"]["objects_detected"] = objects_detected
        self.data["lidar"]["point_cloud_density"] = self._generate_value(100, 20) if objects_detected > 0 else 0

        # Simulate Spectrometer
        if random.random() < 0.1: # 10% chance to find something interesting
            self.data["spectrometer"]["composition"] = {
                "H2O": self._generate_value(10, 5),
                "Fe": self._generate_value(5, 2),
                "Si": self._generate_value(20, 8)
            }
            self.data["spectrometer"]["signal_strength"] = self._generate_value(0.8, 0.2)
        else:
            self.data["spectrometer"]["composition"] = {}
            self.data["spectrometer"]["signal_strength"] = 0

        # Simulate Magnetometer
        self.data["magnetometer"]["field_strength"] = self._generate_value(50, 5) # microteslas
        self.data["magnetometer"]["vector"] = [
            self._generate_value(0, 1),
            self._generate_value(0, 1),
            self._generate_value(0, 1)
        ]

    def validate(self):
        super().validate()
        if self.data["lidar"]["point_cloud_density"] > 200:
            self.data["status"] = "WARNING"
            self._add_error("High point cloud density, potential sensor overload.")
