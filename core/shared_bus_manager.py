import json
import os
import fcntl # Import fcntl for file locking
from datetime import datetime
from typing import Dict, List, Any

# Define the path to the shared bus file
# Assuming it's in the project root, as per previous analysis and prompt's implied location
SHARED_BUS_FILE_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'shared_bus.json'))

class SharedBusManager:
    def __init__(self):
        self._bus_data: Dict[str, Dict[str, Any]] = self.load_bus()
        print(f"[SharedBusManager] Initialized. Loaded {len(self._bus_data)} agents.")

    def load_bus(self) -> Dict[str, Dict[str, Any]]:
        """Loads the shared bus data from shared_bus.json with file locking."""
        if not os.path.exists(SHARED_BUS_FILE_PATH):
            print(f"[SharedBusManager] {SHARED_BUS_FILE_PATH} not found. Creating with empty structure.")
            self.save_bus({}) # This will create the file with an empty dict
            return {}
        
        data = {}
        try:
            with open(SHARED_BUS_FILE_PATH, 'r') as f:
                fcntl.flock(f, fcntl.LOCK_SH) # Acquire a shared lock
                try:
                    content = f.read()
                    if not content.strip():
                        print(f"[SharedBusManager] {SHARED_BUS_FILE_PATH} is empty. Initializing with empty structure.")
                        data = {}
                    else:
                        data = json.loads(content)
                except (json.JSONDecodeError, IOError) as e:
                    print(f"[SharedBusManager] Error reading or parsing {SHARED_BUS_FILE_PATH}: {e}. Resetting to empty structure.")
                    data = {}
                finally:
                    fcntl.flock(f, fcntl.LOCK_UN) # Release the lock
        except IOError as e:
            print(f"[SharedBusManager] Failed to open {SHARED_BUS_FILE_PATH} for reading: {e}. Resetting to empty structure.")
            data = {}
        return data

    def save_bus(self, data: Dict[str, Dict[str, Any]]):
        """Saves the current shared bus data to shared_bus.json with atomic write and file locking."""
        temp_file_path = SHARED_BUS_FILE_PATH + ".tmp"
        try:
            with open(temp_file_path, 'w') as f:
                fcntl.flock(f, fcntl.LOCK_EX) # Acquire an exclusive lock on the temp file
                json.dump(data, f, indent=2)
                f.flush() # Ensure all data is written to disk
                os.fsync(f.fileno()) # Ensure file is physically written
                fcntl.flock(f, fcntl.LOCK_UN) # Release the lock
            os.replace(temp_file_path, SHARED_BUS_FILE_PATH) # Atomic rename
            print(f"[SharedBusManager] Successfully saved data to {SHARED_BUS_FILE_PATH}.")
            self._bus_data = data # Update internal state after successful save
        except IOError as e:
            print(f"[SharedBusManager] Error writing to {SHARED_BUS_FILE_PATH}: {e}")
        except Exception as e:
            print(f"[SharedBusManager] An unexpected error occurred during saving {SHARED_BUS_FILE_PATH}: {e}")
        finally:
            if os.path.exists(temp_file_path):
                os.remove(temp_file_path) # Clean up temp file in case of error

    def get_agent(self, agent_id: str) -> Dict[str, Any]:
        """Returns the profile of a specific agent."""
        # Reload bus data to ensure freshest state before getting agent
        self._bus_data = self.load_bus()
        agent_profile = self._bus_data.get(agent_id, {})
        print(f"[SharedBusManager] Retrieved agent '{agent_id}': {agent_profile}")
        return agent_profile

    def update_agent(self, agent_id: str, update_data: Dict[str, Any]):
        """Updates an agent's profile or creates it if it doesn't exist."""
        # Reload bus data to ensure freshest state before updating
        self._bus_data = self.load_bus()
        current_agent_data = self._bus_data.get(agent_id, {})
        
        # Merge update_data into current_agent_data
        # This handles nested dictionaries by updating them, not overwriting
        def _recursive_update(target, source):
            for key, value in source.items():
                if isinstance(value, dict) and key in target and isinstance(target[key], dict):
                    _recursive_update(target[key], value)
                else:
                    target[key] = value
        
        _recursive_update(current_agent_data, update_data)
        
        # Add/update last_update timestamp
        current_agent_data["last_update"] = datetime.now().isoformat()

        self._bus_data[agent_id] = current_agent_data
        self.save_bus(self._bus_data)
        print(f"[SharedBusManager] Updated agent '{agent_id}'.")

    def delete_agent(self, agent_id: str):
        """Deletes an agent's profile from the shared bus."""
        # Reload bus data to ensure freshest state before deleting
        self._bus_data = self.load_bus()
        if agent_id in self._bus_data:
            del self._bus_data[agent_id]
            self.save_bus(self._bus_data)
            print(f"[SharedBusManager] Deleted agent '{agent_id}'.")
        else:
            print(f"[SharedBusManager] Agent '{agent_id}' not found for deletion.")

    def list_agents(self) -> List[str]:
        """Returns a list of all agent IDs in the shared bus."""
        # Reload bus data to ensure freshest state before listing
        self._bus_data = self.load_bus()
        agent_ids = list(self._bus_data.keys())
        print(f"[SharedBusManager] Listed agents: {agent_ids}")
        return agent_ids

# Example usage (for testing this module directly)
if __name__ == "__main__":
    print("--- SharedBusManager Test (Prompt 4) ---")

    # Clean up old shared_bus.json for a fresh start
    if os.path.exists(SHARED_BUS_FILE_PATH):
        os.remove(SHARED_BUS_FILE_PATH)
        print(f"Cleaned up existing {SHARED_BUS_FILE_PATH} for test.")

    manager = SharedBusManager()

    # Test update_agent (add new agent)
    manager.update_agent("QIKI-01", {
        "state": "active",
        "battery": 84.0,
        "task": "mapping",
        "capabilities": ["move", "scan", "lift"],
        "link_status": "connected",
        "position": {"x": 1.0, "y": 2.5, "z": 0.0}
    })

    # Test update_agent (add another agent)
    manager.update_agent("QIKI-02", {
        "state": "idle",
        "battery": 99.0,
        "task": "standby",
        "capabilities": ["listen"],
        "link_status": "disconnected",
        "position": {"x": 0.0, "y": 0.0, "z": 0.0}
    })

    # Test get_agent
    agent1_data = manager.get_agent("QIKI-01")
    print(f"\nRetrieved QIKI-01: {agent1_data}")

    # Test list_agents
    all_agent_ids = manager.list_agents()
    print(f"\nAll agent IDs: {all_agent_ids}")

    # Test update_agent (modify existing agent)
    manager.update_agent("QIKI-01", {"battery": 80.5, "task": "exploring"})
    print(f"\nUpdated QIKI-01: {manager.get_agent('QIKI-01')}")

    # Test delete_agent
    manager.delete_agent("QIKI-02")
    print(f"\nAll agent IDs after deletion: {manager.list_agents()}")
    print(f"QIKI-02 after deletion: {manager.get_agent('QIKI-02')}")

    # Test loading from existing file after operations
    manager2 = SharedBusManager()
    print(f"\nManager2 loaded data: {manager2._bus_data}")

    print("--- SharedBusManager Test Complete ---")
