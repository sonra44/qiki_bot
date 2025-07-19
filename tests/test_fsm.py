import os
import sys

# Add the project root to the sys.path so core modules can be imported
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(PROJECT_ROOT)

from core.fsm_core import FiniteStateMachine


def _make_fsm() -> FiniteStateMachine:
    """Create a FiniteStateMachine instance with the default transitions."""
    transitions = {
        "IDLE": {"START_MISSION": "MISSION_ACTIVE", "CHARGE": "CHARGING"},
        "MISSION_ACTIVE": {
            "PAUSE_MISSION": "IDLE",
            "END_MISSION": "IDLE",
            "OBSTACLE_DETECTED": "AVOIDING",
        },
        "CHARGING": {"CHARGE_COMPLETE": "IDLE"},
        "AVOIDING": {"OBSTACLE_CLEARED": "MISSION_ACTIVE"},
        "ERROR": {"RESET": "IDLE"},
    }
    return FiniteStateMachine(initial_state="IDLE", transitions=transitions)


def test_fsm_transitions():
    fsm = _make_fsm()
    assert fsm.get_current_state() == "IDLE"

    assert fsm.trigger_event("START_MISSION")
    assert fsm.get_current_state() == "MISSION_ACTIVE"

    assert fsm.trigger_event("OBSTACLE_DETECTED")
    assert fsm.get_current_state() == "AVOIDING"

    assert fsm.trigger_event("OBSTACLE_CLEARED")
    assert fsm.get_current_state() == "MISSION_ACTIVE"

    assert fsm.trigger_event("END_MISSION")
    assert fsm.get_current_state() == "IDLE"
