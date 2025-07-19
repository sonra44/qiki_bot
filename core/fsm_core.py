
# -*- coding: utf-8 -*-
"""
QIKI Bot
Finite State Machine (FSM) Core Logic
"""
import time


class FiniteStateMachine:
    """
    A pure, in-memory Finite State Machine core.
    It handles states, transitions, and events without any I/O operations.
    """

    def __init__(self, initial_state="UNKNOWN", transitions=None):
        self.current_state = initial_state
        self.transitions = transitions if transitions is not None else {}
        self.state_register = {initial_state: {"enter_time": time.time(), "exit_time": None}}
        self.last_event = None
        self.last_event_time = None
        self.history = []

    def trigger_event(self, event, meta=None):
        """
        Triggers a state transition based on an event.
        Returns True if the state changed, False otherwise.
        """
        if self.current_state in self.transitions and event in self.transitions[self.current_state]:
            old_state = self.current_state
            new_state = self.transitions[self.current_state][event]

            # Update state register for the old state
            if old_state in self.state_register:
                self.state_register[old_state]["exit_time"] = time.time()

            # Set the new state
            self.current_state = new_state
            self.last_event = event
            self.last_event_time = time.time()

            # Create a new entry for the new state
            self.state_register[new_state] = {"enter_time": time.time(), "exit_time": None, "triggered_by": event, "meta": meta}
            
            self.history.append({
                "timestamp": time.time(),
                "from_state": old_state,
                "to_state": new_state,
                "event": event,
                "meta": meta
            })
            
            return True
        return False

    def get_current_state(self):
        """Returns the current state of the FSM."""
        return self.current_state

    def get_possible_transitions(self):
        """Returns a list of possible events from the current state."""
        return list(self.transitions.get(self.current_state, {}).keys())

    def load_state(self, state_dict):
        """Loads the FSM state from a dictionary."""
        self.current_state = state_dict.get("current_state", "UNKNOWN")
        self.transitions = state_dict.get("transitions", {})
        self.state_register = state_dict.get("state_register", {})
        self.last_event = state_dict.get("last_event")
        self.last_event_time = state_dict.get("last_event_time")
        self.history = state_dict.get("history", [])

    def export_state(self):
        """Exports the FSM state to a dictionary."""
        return {
            "current_state": self.current_state,
            "last_event": self.last_event,
            "last_event_time": self.last_event_time,
            "state_duration": time.time() - self.state_register.get(self.current_state, {}).get("enter_time", time.time()),
            "possible_transitions": self.get_possible_transitions(),
            "transitions": self.transitions,
            "state_register": self.state_register,
            "history": self.history
        }

