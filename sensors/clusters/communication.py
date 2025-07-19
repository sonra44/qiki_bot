import random
from .base_cluster import BaseSensorCluster

class CommunicationCluster(BaseSensorCluster):
    def __init__(self):
        super().__init__(cluster_name="Communication")
        self.data.update({
            "signal_strength": {"rssi": -75.0, "snr": 15.0},
            "antenna": {"azimuth": 180.0, "elevation": 45.0, "is_tracking": True},
            "data_link": {"ber": 1e-6, "bandwidth_mbps": 100.0}
        })

    def update(self):
        self.data["signal_strength"]["rssi"] = self._generate_value(-75.0, 10.0)
        self.data["signal_strength"]["snr"] = self._generate_value(15.0, 5.0)
        self.data["antenna"]["is_tracking"] = random.random() > 0.05 # 95% chance to be tracking
        self.data["data_link"]["ber"] = self._generate_value(1e-6, 1e-7)

    def validate(self):
        super().validate()
        rssi = self.data["signal_strength"]["rssi"]
        if rssi < -90:
            self.data["status"] = "ERROR"
            self._add_error(f"Signal strength critical (RSSI: {rssi:.1f} dBm)")
        elif rssi < -80:
            self.data["status"] = "WARNING"
            self._add_error(f"Signal strength low (RSSI: {rssi:.1f} dBm)")

        if not self.data["antenna"]["is_tracking"]:
            self.data["status"] = "WARNING"
            self._add_error("Antenna is not tracking target.")
