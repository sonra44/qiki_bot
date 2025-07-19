import json
import time
import os
import sys
from datetime import datetime

# Add project root to sys.path for imports
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.append(project_root)

from core.file_paths import SENSORS_FILE, SENSOR_LOG_FILE
# Import all cluster classes
from sensors.clusters.navigation import NavigationCluster
from sensors.clusters.power import PowerCluster
from sensors.clusters.thermal import ThermalCluster
from sensors.clusters.communication import CommunicationCluster
from sensors.clusters.structural import StructuralCluster
from sensors.clusters.rlsm import RLSMCluster
from sensors.clusters.proximity import ProximityCluster
from sensors.clusters.thrusters import ThrusterCluster
from sensors.clusters.environment import EnvironmentCluster
from sensors.clusters.system_health import SystemHealthCluster
from sensors.clusters.ew import EWCluster

class SensorBus:
    def __init__(self):
        self.clusters = {
            # Core Systems
            "navigation": NavigationCluster(),
            "power": PowerCluster(),
            "thermal": ThermalCluster(),
            "structural": StructuralCluster(),
            "system_health": SystemHealthCluster(),
            "thrusters": ThrusterCluster(),
            # External Perception
            "rlsm": RLSMCluster(),
            "proximity": ProximityCluster(),
            "environment": EnvironmentCluster(),
            # Communication & EW
            "communication": CommunicationCluster(),
            "ew": EWCluster(),
        }
        self._setup_logging()
        self._log("SensorBus initialized with all clusters.")

    def _setup_logging(self):
        self.log_file = SENSOR_LOG_FILE
        os.makedirs(os.path.dirname(self.log_file), exist_ok=True)

    def _log(self, message):
        timestamp = datetime.now().isoformat()
        with open(self.log_file, 'a') as f:
            f.write(f"[{timestamp}] [SensorBus] {message}\n")

    def run(self):
        self._log("SensorBus process started.")
        while True:
            try:
                full_sensor_data = {}
                active_clusters = 0

                for name, cluster in self.clusters.items():
                    try:
                        cluster.update()
                    except Exception as e:  # noqa: BLE001
                        cluster.data["status"] = "FAIL"
                        cluster._add_error(f"Update failed: {e}")
                        self._log(
                            f"ERROR: Cluster '{cluster.get_name()}' update failed: {e}"
                        )

                    cluster.validate()  # Run validation after update
                    full_sensor_data[name] = cluster.serialize()
                    
                    status = cluster.data.get("status", "UNKNOWN")
                    if status == "ERROR":
                        self._log(f"CRITICAL: Cluster '{cluster.get_name()}' reported an ERROR state.")
                    elif status == "WARNING":
                        self._log(f"WARNING: Cluster '{cluster.get_name()}' reported a WARNING state.")
                    
                    active_clusters += 1

                # Atomically write to the main sensors file
                temp_filepath = f"{SENSORS_FILE}.tmp"
                with open(temp_filepath, 'w') as f:
                    json.dump(full_sensor_data, f, indent=4)
                os.rename(temp_filepath, SENSORS_FILE)
                
                self._log(f"Successfully updated and validated {active_clusters}/{len(self.clusters)} clusters.")
                time.sleep(2) # Update interval

            except KeyboardInterrupt:
                self._log("SensorBus process terminated by user.")
                break
            except Exception as e:
                self._log(f"CRITICAL RUNTIME ERROR: {e}")
                import traceback
                self._log(traceback.format_exc())
                time.sleep(10) # Wait before retrying

if __name__ == "__main__":
    bus = SensorBus()
    bus.run()
