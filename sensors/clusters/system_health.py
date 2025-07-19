import random
from .base_cluster import BaseSensorCluster

class SystemHealthCluster(BaseSensorCluster):
    def __init__(self):
        super().__init__(cluster_name="SystemHealth")
        self.data.update({
            "data_bus": {"load_percentage": 15, "errors_per_minute": 0},
            "processor": {"load_percentage": 25, "core_voltage": 1.1},
            "memory": {"ram_used_percentage": 40, "ecc_errors": 0}
        })

    def update(self):
        # Simulate Data Bus
        self.data["data_bus"]["load_percentage"] = self._generate_value(15, 5)
        self.data["data_bus"]["errors_per_minute"] = random.randint(0, 2) if random.random() < 0.05 else 0

        # Simulate Processor
        self.data["processor"]["load_percentage"] = self._generate_value(25, 10)
        self.data["processor"]["core_voltage"] = self._generate_value(1.1, 0.05)

        # Simulate Memory
        self.data["memory"]["ram_used_percentage"] = self._generate_value(40, 15)
        if random.random() < 0.01:
            self.data["memory"]["ecc_errors"] += 1

    def validate(self):
        super().validate()
        if self.data["data_bus"]["errors_per_minute"] > 5:
            self.data["status"] = "ERROR"
            self._add_error("High data bus error rate.")

        if self.data["memory"]["ecc_errors"] > 10:
            self.data["status"] = "ERROR"
            self._add_error("Multiple ECC memory errors detected.")

        if self.data["processor"]["load_percentage"] > 90:
            self.data["status"] = "WARNING"
            self._add_error("High processor load.")
