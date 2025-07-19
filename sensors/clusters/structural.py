import random
from .base_cluster import BaseSensorCluster

class StructuralCluster(BaseSensorCluster):
    def __init__(self):
        super().__init__(cluster_name="Structural")
        self.data.update({
            "strain_gauges": {"hull_main": 0.1, "solar_panel_joint": 0.05},
            "vibration": {"x_axis": 0.01, "y_axis": 0.02, "z_axis": 0.01},
            "hull_pressure": {"internal": 101.3, "external": 0.0}
        })

    def update(self):
        self.data["strain_gauges"]["hull_main"] = self._generate_value(0.1, 0.02)
        self.data["vibration"]["x_axis"] = self._generate_value(0.01, 0.005)
        self.data["hull_pressure"]["internal"] = self._generate_value(101.3, 0.1)

    def validate(self):
        super().validate()
        strain = self.data["strain_gauges"]["hull_main"]
        if strain > 0.5:
            self.data["status"] = "ERROR"
            self._add_error(f"Critical hull strain detected: {strain:.3f}")
        elif strain > 0.3:
            self.data["status"] = "WARNING"
            self._add_error(f"High hull strain detected: {strain:.3f}")
