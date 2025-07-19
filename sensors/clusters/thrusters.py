import random
from .base_cluster import BaseSensorCluster

class ThrusterCluster(BaseSensorCluster):
    def __init__(self):
        super().__init__(cluster_name="Thrusters")
        self.data.update({
            "thrusters": {
                "main_engine": {"thrust": 0, "fuel_flow": 0, "temperature": 15},
                "rcs_quad_a": {"thrust": 0, "temperature": 15},
                "rcs_quad_b": {"thrust": 0, "temperature": 15}
            },
            "gimbal": {"main_engine_pitch": 0, "main_engine_yaw": 0}
        })

    def update(self):
        # Simulate Main Engine
        main_thrust = self._generate_value(100, 10) if random.random() < 0.05 else 0 # 5% chance of main engine burn
        self.data["thrusters"]["main_engine"]["thrust"] = main_thrust
        self.data["thrusters"]["main_engine"]["fuel_flow"] = main_thrust * 1.5 if main_thrust > 0 else 0
        self.data["thrusters"]["main_engine"]["temperature"] = self._generate_value(1500, 200) if main_thrust > 0 else 15

        # Simulate RCS
        self.data["thrusters"]["rcs_quad_a"]["thrust"] = self._generate_value(5, 2) if random.random() < 0.3 else 0
        self.data["thrusters"]["rcs_quad_b"]["thrust"] = self._generate_value(5, 2) if random.random() < 0.3 else 0

        # Simulate Gimbal
        if main_thrust > 0:
            self.data["gimbal"]["main_engine_pitch"] = self._generate_value(0, 2.5)
            self.data["gimbal"]["main_engine_yaw"] = self._generate_value(0, 2.5)

    def validate(self):
        super().validate()
        temp = self.data["thrusters"]["main_engine"]["temperature"]
        if temp > 2000:
            self.data["status"] = "ERROR"
            self._add_error(f"Main engine temperature critical: {temp:.0f}C")
