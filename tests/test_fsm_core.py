import os
import sys

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(PROJECT_ROOT)

from core.fsm_core import FiniteStateMachine


TRANSITIONS = {
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


def test_export_and_load():
    fsm = FiniteStateMachine(initial_state="IDLE", transitions=TRANSITIONS)
    assert fsm.trigger_event("START_MISSION")
    exported = fsm.export_state()

    new_fsm = FiniteStateMachine()
    new_fsm.load_state(exported)
    assert new_fsm.get_current_state() == "MISSION_ACTIVE"
    assert new_fsm.history[0]["event"] == "START_MISSION"
