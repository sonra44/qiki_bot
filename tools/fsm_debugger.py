
# -*- coding: utf-8 -*-
"""
QIKI Bot
FSM Debugger Tool
"""
import json
import os
import sys

# Add the project root to the python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.fsm_io import enqueue_event
from core.fsm_client import FSMClient

fsm_client = FSMClient()

def print_status():
    """Prints the current FSM state."""
    state = fsm_client.get_state()
    print(json.dumps(state, indent=4))

def step_fsm(event):
    """Sends an event to the FSM."""
    print(f"Injecting event: {event}")
    enqueue_event(event, source="fsm_debugger")

def list_transitions():
    """Lists the possible transitions from the current state."""
    state = fsm_client.get_state()
    if 'possible_transitions' in state:
        print("Possible transitions:")
        for transition in state['possible_transitions']:
            print(f"- {transition}")
    else:
        print("Could not determine possible transitions from the current state.")

def force_state(state):
    """Forces the FSM to a specific state."""
    print(f"Forcing state to: {state}. This is a dangerous operation and is not recommended.")
    # This is not implemented as it is a dangerous operation
    # and requires direct manipulation of the fsm_state.json file.

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python tools/fsm_debugger.py [status|step <EVENT>|list|inject_event <EVENT>|force_state <STATE>]")
        sys.exit(1)

    command = sys.argv[1]

    if command == "status":
        print_status()
    elif command == "step" and len(sys.argv) > 2:
        step_fsm(sys.argv[2])
    elif command == "list":
        list_transitions()
    elif command == "inject_event" and len(sys.argv) > 2:
        step_fsm(sys.argv[2])
    elif command == "force_state" and len(sys.argv) > 2:
        force_state(sys.argv[2])
    else:
        print(f"Unknown command or missing argument: {command}")
