import random
from .base_cluster import BaseSensorCluster

class ThermalCluster(BaseSensorCluster):
    def __init__(self):
        super().__init__(cluster_name="Thermal")
        self.data.update({
            "core_temp": {"cpu": 45.0, "gpu": 55.0},
            "radiators": {"panel_a_temp": -10.0, "panel_b_temp": -12.5},
            "heat_pipes": {"flow_rate": 1.5, "pressure": 2.1}
        })

    def update(self):
        self.data["core_temp"]["cpu"] = self._generate_value(45.0, 2.0)
        self.data["core_temp"]["gpu"] = self._generate_value(55.0, 3.0)
        self.data["radiators"]["panel_a_temp"] = self._generate_value(-10.0, 5.0)
        self.data["radiators"]["panel_b_temp"] = self._generate_value(-12.5, 5.0)
        self.data["heat_pipes"]["flow_rate"] = self._generate_value(1.5, 0.1)
        self.data["heat_pipes"]["pressure"] = self._generate_value(2.1, 0.1)

    def validate(self):
        super().validate()
        cpu_temp = self.data["core_temp"]["cpu"]
        gpu_temp = self.data["core_temp"]["gpu"]
        if cpu_temp > 85 or gpu_temp > 95:
            self.data["status"] = "ERROR"
            self._add_error(f"Core temperature critical: CPU {cpu_temp:.1f}C, GPU {gpu_temp:.1f}C")
        elif cpu_temp > 70 or gpu_temp > 80:
            self.data["status"] = "WARNING"
            self._add_error(f"Core temperature high: CPU {cpu_temp:.1f}C, GPU {gpu_temp:.1f}C")
