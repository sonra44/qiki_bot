import sys
import os

# Add the project root to the sys.path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(project_root)

from core.fsm import SimpleFSM

def test_fsm_transitions():
    fsm = SimpleFSM()
    fsm.boot_complete()
    assert fsm.state == "idle"
    fsm.start_navigation()
    assert fsm.state == "navigating"
    fsm.start_processing()
    assert fsm.state == "processing"
    fsm.low_power()
    assert fsm.state == "charging"
    fsm.charged()
    assert fsm.state == "idle"
