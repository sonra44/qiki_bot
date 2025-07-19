import random
from .base_cluster import BaseSensorCluster

class PowerCluster(BaseSensorCluster):
    def __init__(self):
        super().__init__(cluster_name="Power")
        self.data.update({
            "battery_main": {"voltage": 12.5, "current": -1.2, "temperature": 25.0, "soc": 98.0},
            "solar_panels": {"voltage": 20.1, "current": 2.5, "is_charging": True},
            "power_bus": {"main_bus_voltage": 12.4, "load_current": 3.7}
        })

    def update(self):
        # Simulate Battery
        self.data["battery_main"]["voltage"] = self._generate_value(12.5, 0.2)
        self.data["battery_main"]["current"] = self._generate_value(-1.2, 0.5)
        self.data["battery_main"]["temperature"] = self._generate_value(25.0, 1.0)
        self.data["battery_main"]["soc"] = max(0, self.data["battery_main"]["soc"] - 0.01) # Slow discharge

        # Simulate Solar Panels
        is_charging = random.random() > 0.3 # 70% chance to be in sun
        self.data["solar_panels"]["is_charging"] = is_charging
        self.data["solar_panels"]["voltage"] = self._generate_value(20.0, 1.5) if is_charging else 0.0
        self.data["solar_panels"]["current"] = self._generate_value(2.5, 0.5) if is_charging else 0.0

        # Simulate Power Bus
        self.data["power_bus"]["main_bus_voltage"] = self.data["battery_main"]["voltage"] - 0.1
        self.data["power_bus"]["load_current"] = abs(self.data["battery_main"]["current"]) + self.data["solar_panels"]["current"] + self._generate_value(2.0, 0.1)

    def validate(self):
        super().validate()
        soc = self.data["battery_main"]["soc"]
        if soc < 20:
            self.data["status"] = "ERROR"
            self._add_error(f"Main battery SOC critical: {soc:.1f}%")
        elif soc < 50:
            self.data["status"] = "WARNING"
            self._add_error(f"Main battery SOC low: {soc:.1f}%")

        if self.data["battery_main"]["temperature"] > 50:
            self.data["status"] = "ERROR"
            self._add_error(f"Battery temperature critical: {self.data['battery_main']['temperature']:.1f}C")
