import random
from .base_cluster import BaseSensorCluster

class EnvironmentCluster(BaseSensorCluster):
    def __init__(self):
        super().__init__(cluster_name="Environment")
        self.data.update({
            "radiation_detector": {"level_sv": 0.002, "is_alert": False},
            "micrometeorite_detector": {"impacts_last_hour": 0, "last_impact_energy_j": 0},
            "plasma_density": {"density_cm3": 5.0}
        })

    def update(self):
        # Simulate Radiation
        rad_level = self._generate_value(0.002, 0.001) if random.random() > 0.01 else self._generate_value(0.1, 0.05)
        self.data["radiation_detector"]["level_sv"] = rad_level
        self.data["radiation_detector"]["is_alert"] = rad_level > 0.05

        # Simulate Micrometeorites
        if random.random() < 0.01: # 1% chance of impact
            self.data["micrometeorite_detector"]["impacts_last_hour"] += 1
            self.data["micrometeorite_detector"]["last_impact_energy_j"] = self._generate_value(0.1, 0.08)
        
        # Simulate Plasma Density
        self.data["plasma_density"]["density_cm3"] = self._generate_value(5.0, 2.0)

    def validate(self):
        super().validate()
        if self.data["radiation_detector"]["is_alert"]:
            self.data["status"] = "ERROR"
            self._add_error(f"High radiation levels detected: {self.data['radiation_detector']['level_sv']:.4f} Sv/h")
        
        if self.data["micrometeorite_detector"]["last_impact_energy_j"] > 0.5:
            self.data["status"] = "WARNING"
            self._add_error("High energy micrometeorite impact detected.")
