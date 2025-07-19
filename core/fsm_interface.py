
# -*- coding: utf-8 -*-
"""
QIKI Bot
FSM Interface - Handles all I/O for the FSM.
"""
import json
import time
import os
from .fsm_core import FiniteStateMachine
from .fsm_client import FSMClient

# Assuming shared_json_cache and system_logger are available
# from .shared_json_cache import SharedJSONCache
# from .system_logger import SystemLogger

class FSMInterface:
    """
    Manages the FSM's state persistence and interaction with the filesystem.
    """
    def __init__(self, fsm_state_file, mission_file=None):
        self.fsm_state_file = fsm_state_file
        self.mission_file = mission_file
        self.fsm = self._load_or_initialize_fsm()
        # self.logger = SystemLogger("FSM_Interface")

    def _load_or_initialize_fsm(self):
        """Loads the FSM state from file or initializes a new one using FSMClient."""
        fsm_client = FSMClient()
        state_data = fsm_client.get_state()
        
        if state_data and not state_data.get("error"): # Check if state_data is valid and not an error state
            fsm = FiniteStateMachine()
            fsm.load_state(state_data)
            return fsm
        
        # Default transitions if no mission or state file or if there was an error loading state
        default_transitions = {
            "IDLE": {"START_MISSION": "MISSION_ACTIVE", "CHARGE": "CHARGING"},
            "MISSION_ACTIVE": {"PAUSE_MISSION": "IDLE", "END_MISSION": "IDLE", "OBSTACLE_DETECTED": "AVOIDING"},
            "CHARGING": {"CHARGE_COMPLETE": "IDLE"},
            "AVOIDING": {"OBSTACLE_CLEARED": "MISSION_ACTIVE"},
            "ERROR": {"RESET": "IDLE"}
        }
        return FiniteStateMachine(initial_state="IDLE", transitions=default_transitions)

    def sync_state_to_disk(self):
        """Exports the current FSM state and writes it to the JSON file using FSMClient."""
        state_dict = self.fsm.export_state()
        fsm_client = FSMClient()
        meta = {"trigger": "sync_to_disk", "context": state_dict, "source": "FSMInterface"}
        fsm_client.set_state(state_dict.get("current_state", "UNKNOWN"), meta)

    def trigger_event(self, event, meta=None):
        """
        Triggers an event in the FSM core and syncs the new state to disk.
        """
        # self.logger.log(f"Attempting to trigger event: '{event}' with meta: {meta}")
        if self.fsm.trigger_event(event, meta):
            # self.logger.log(f"Event '{event}' successful. State changed to {self.fsm.get_current_state()}")
            self.sync_state_to_disk()
            return True
        # self.logger.log(f"Event '{event}' had no effect on state {self.fsm.get_current_state()}", level="WARNING")
        return False

    def get_status(self):
        """Returns the full exported state of the FSM."""
        return self.fsm.export_state()

# Example of how to use it with a CLI
if __name__ == '__main__':
    import sys

    fsm_interface = FSMInterface(fsm_state_file=None) # fsm_state_file is no longer directly used here
    fsm_client = FSMClient()

    if len(sys.argv) > 1:
        command = sys.argv[1]
        if command == "status":
            print(json.dumps(fsm_client.get_state(), indent=4))
        elif command == "trigger" and len(sys.argv) > 2:
            event_name = sys.argv[2]
            # The trigger_event method in FSMInterface now internally uses FSMClient
            if fsm_interface.trigger_event(event_name):
                print(f"Successfully triggered event: {event_name}")
                print("New state:")
                print(json.dumps(fsm_client.get_state(), indent=4))
            else:
                print(f"Failed to trigger event: {event_name}")
        else:
            print(f"Unknown command or missing argument. Usage: python {sys.argv[0]} [status|trigger <EVENT>] ")
    else:
        print(f"Usage: python {sys.argv[0]} [status|trigger <EVENT>] ")
