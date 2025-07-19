import os
import json
import time
import random

# Add project root to sys.path for imports
import sys
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.append(project_root)

from core.telemetry import TelemetryManager
from core.fsm_core import FiniteStateMachine
from core.fsm_client import FSMClient
from core.file_paths import TELEMETRY_FILE, FSM_STATE_FILE

class PhysicsEngine:
    def __init__(self):
        # Load physical parameters from bot_specs.json
        self._load_specs()

        # Dynamic state variables (initialized from telemetry or defaults)
        # These will be loaded from file in update_physics()
        self.velocity = 0.0
        self.acceleration = 0.0
        self.impulse_active = False
        self.power_wh = self.power_capacity_wh
        self.consumption_w = 0.0
        self.battery_percent = 100.0

        print("PhysicsEngine initialized with specs:", self.specs)

    def _load_specs(self):
        specs_path = os.path.join(project_root, 'config', 'bot_specs.json')
        try:
            with open(specs_path, 'r') as f:
                self.specs = json.load(f)
                bot_physical = self.specs.get('bot', {}).get('physical', {})
                bot_power = bot_physical.get('power', {})
                
                # Assign specs to class attributes, with fallbacks
                self.mass_kg = bot_physical.get('mass_kg', 35.0)
                self.max_speed_mps = bot_physical.get('max_speed_mps', 1.2)
                self.power_capacity_wh = bot_power.get('capacity_wh', 500.0)
                self.consumption_w_idle = bot_power.get('consumption_w_idle', 5.0)
                self.consumption_w_max = bot_power.get('consumption_w_max', 120.0)

        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"[ERROR] Could not load or parse bot_specs.json: {e}. Using default values.")
            self.specs = {}
            self.mass_kg = 35.0
            self.max_speed_mps = 1.2
            self.power_capacity_wh = 500.0
            self.consumption_w_idle = 5.0
            self.consumption_w_max = 120.0

        # Dynamic state variables (initialized from telemetry or defaults)
        # These will be loaded from file in update_physics()
        self.velocity = 0.0
        self.acceleration = 0.0
        self.impulse_active = False
        self.power_wh = self.power_capacity_wh
        self.consumption_w = 0.0
        self.battery_percent = 100.0

        print("PhysicsEngine initialized.")

    def update_physics(self):
        # Load current state from files
        telemetry_manager = TelemetryManager()
        fsm_client = FSMClient()

        current_telemetry = telemetry_manager.get()
        current_fsm_state_obj = fsm_client.get_state()
        current_fsm_state = current_fsm_state_obj.get("mode", "unknown") # Assuming 'mode' is the key for the current state

        # Update internal state from loaded telemetry
        self.velocity = current_telemetry.get("velocity", 0.0)
        self.acceleration = current_telemetry.get("acceleration", 0.0)
        self.impulse_active = current_telemetry.get("impulse_active", False)
        self.power_wh = current_telemetry.get("power_wh", self.power_capacity_wh)
        self.consumption_w = current_telemetry.get("consumption_w", 0.0)
        self.battery_percent = current_telemetry.get("battery_percent", 100.0)

        prev_velocity = self.velocity

        # Reset values for current tick
        self.acceleration = 0.0
        self.consumption_w = 0.0

        if current_fsm_state == "idle":
            self.velocity = 0.0
            self.impulse_active = False
            self.consumption_w = self.consumption_w_idle # Use idle consumption from specs
        elif current_fsm_state == "moving":
            # Increase velocity towards max_speed
            target_velocity = self.max_speed_mps
            if self.velocity < target_velocity:
                self.velocity = min(target_velocity, self.velocity + 0.2) # Increase by 0.2 m/s per second
            
            self.consumption_w = 10.0 # Base consumption for moving
            self.impulse_active = random.choice([True, False]) # Random impulse
            if self.impulse_active:
                self.consumption_w += 50.0 # Additional consumption for impulse

        elif current_fsm_state == "charging":
            self.velocity = 0.0
            self.impulse_active = False
            # Battery grows by 2% of capacity per second
            charge_rate_wh_per_sec = self.power_capacity_wh * 0.02
            self.power_wh = min(self.power_capacity_wh, self.power_wh + charge_rate_wh_per_sec)
            self.consumption_w = -charge_rate_wh_per_sec # Negative consumption for charging

        elif current_fsm_state == "error":
            self.velocity = 0.0
            self.impulse_active = False
            self.consumption_w = 0.0 # No consumption in error state

        # Calculate acceleration based on velocity change
        self.acceleration = self.velocity - prev_velocity

        # Update power_wh based on consumption (for 1 second tick)
        # Only decrease power_wh if not charging (charging handled above)
        if current_fsm_state != "charging":
            energy_consumed_wh_per_sec = self.consumption_w / 3600.0 # Convert W to Wh for 1 second
            self.power_wh -= energy_consumed_wh_per_sec

        # Clamp power_wh between 0 and capacity
        self.power_wh = max(0.0, min(self.power_wh, self.power_capacity_wh))
        self.battery_percent = (self.power_wh / self.power_capacity_wh) * 100.0

        # Prepare telemetry data
        telemetry_data = {
            "velocity": round(self.velocity, 2),
            "acceleration": round(self.acceleration, 2),
            "impulse_active": self.impulse_active,
            "consumption_w": round(self.consumption_w, 2),
            "power_wh": round(self.power_wh, 2),
            "battery_percent": round(self.battery_percent, 1)
        }

        # Update TelemetryManager
        telemetry_manager.update(telemetry_data)
        print(f"Physics update for FSM state '{current_fsm_state}': {telemetry_data}")

# Main execution block
if __name__ == "__main__":
    print("--- PhysicsEngine Simulation Start ---")

    # Clean up old telemetry.json for a fresh start
    if os.path.exists(TELEMETRY_FILE):
        os.remove(TELEMETRY_FILE)
        print(f"Cleaned up existing {TELEMETRY_FILE} for test.")
    
    # Clean up old fsm_state.json for a fresh start
    # os.remove(FSM_STATE_FILE) # Removed as FSMClient handles initialization
    # print(f"Cleaned up existing {FSM_STATE_FILE} for test.")

    engine = PhysicsEngine()
    
    try:
        while True:
            engine.update_physics()
            time.sleep(1) # Update every 1 second
    except KeyboardInterrupt:
        print("\nPhysicsEngine simulation terminated by user.")
    except Exception as e:
        print(f"An unexpected error occurred in PhysicsEngine: {e}")