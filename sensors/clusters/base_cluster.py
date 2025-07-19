import random

class BaseSensorCluster:
    """
    Base class for all sensor clusters, providing a common interface for 
    initialization, data updates, validation, and serialization.
    """
    def __init__(self, cluster_name: str):
        self.cluster_name = cluster_name
        self.data = {
            "status": "INITIALIZING",
            "last_update_timestamp": None,
            "errors": []
        }

    def get_name(self) -> str:
        """Returns the name of the cluster."""
        return self.cluster_name

    def update(self):
        """
        Updates the sensor data. This is the core logic of the sensor simulation.
        Must be implemented by subclasses.
        """
        raise NotImplementedError("Subclasses must implement the update() method.")

    def validate(self):
        """
        Validates the current sensor data. Can be extended by subclasses 
        to check for anomalies or out-of-range values.
        By default, it just checks if the data dictionary exists.
        """
        if not self.data:
            self.data["status"] = "ERROR"
            self.data["errors"].append("Data dictionary is empty.")
        else:
            # Basic validation passed, specific checks should be in child classes
            self.data["status"] = "OK" 
            self.data["errors"] = [] # Clear previous errors if OK

    def serialize(self) -> dict:
        """Returns the current data of the cluster as a dictionary."""
        return self.data

    def _generate_value(self, base, variance, precision=2):
        """Helper to generate a random value with some variance and precision."""
        return round(base + random.uniform(-variance, variance), precision)

    def _add_error(self, error_message: str):
        """Adds an error message to the list and sets status to ERROR."""
        if error_message not in self.data["errors"]:
            self.data["errors"].append(error_message)
        self.data["status"] = "ERROR"
