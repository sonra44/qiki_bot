import random
from .base_cluster import BaseSensorCluster

class EWCluster(BaseSensorCluster):
    def __init__(self):
        super().__init__(cluster_name="ElectronicWarfare")
        self.data.update({
            "jamming_detector": {"is_jammed": False, "jamming_frequency": 0},
            "signal_interceptor": {"signals_detected": 0, "strongest_signal_db": -120},
            "emcon_monitor": {"current_level": "A", "is_active": True} # A=Silent, B=Low, C=Normal
        })

    def update(self):
        # Simulate Jamming
        is_jammed = random.random() < 0.02 # 2% chance of being jammed
        self.data["jamming_detector"]["is_jammed"] = is_jammed
        self.data["jamming_detector"]["jamming_frequency"] = self._generate_value(1200, 200) if is_jammed else 0

        # Simulate Signal Interception
        signals = random.randint(0, 5)
        self.data["signal_interceptor"]["signals_detected"] = signals
        self.data["signal_interceptor"]["strongest_signal_db"] = self._generate_value(-90, 20) if signals > 0 else -120

    def validate(self):
        super().validate()
        if self.data["jamming_detector"]["is_jammed"]:
            self.data["status"] = "ERROR"
            self._add_error(f"Communications jamming detected!")
