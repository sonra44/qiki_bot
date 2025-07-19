
import unittest
import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.fsm_core import FSMCore

class TestFSMCore(unittest.TestCase):

    def setUp(self):
        """Set up a new FSMCore instance for each test."""
        self.fsm_core = FSMCore()

    def test_initial_state_and_valid_states(self):
        """Test that the list of valid states is correct."""
        self.assertIn("idle", self.fsm_core.get_valid_states())
        self.assertIn("moving", self.fsm_core.get_valid_states())
        self.assertIn("charging", self.fsm_core.get_valid_states())
        self.assertIn("error", self.fsm_core.get_valid_states())

    def test_valid_transition_idle_to_moving(self):
        """Test a standard, valid state transition."""
        new_state = self.fsm_core.trigger("idle", "start_move")
        self.assertEqual(new_state, "moving")

    def test_valid_transition_moving_to_idle(self):
        """Test another standard, valid state transition."""
        new_state = self.fsm_core.trigger("moving", "stop")
        self.assertEqual(new_state, "idle")

    def test_invalid_transition_from_moving(self):
        """Test that an invalid event from a state results in no change."""
        new_state = self.fsm_core.trigger("moving", "charge") # Cannot charge while moving
        self.assertEqual(new_state, "moving")

    def test_transition_to_error_state(self):
        """Test that any state can transition to the error state."""
        self.assertEqual(self.fsm_core.trigger("idle", "error"), "error")
        self.assertEqual(self.fsm_core.trigger("moving", "error"), "error")
        self.assertEqual(self.fsm_core.trigger("charging", "error"), "error")

    def test_reset_from_error_state(self):
        """Test that the FSM can be reset from the error state."""
        new_state = self.fsm_core.trigger("error", "reset")
        self.assertEqual(new_state, "idle")

    def test_nonexistent_event(self):
        """Test that a completely unknown event does not cause a state change."""
        new_state = self.fsm_core.trigger("idle", "launch_fireworks")
        self.assertEqual(new_state, "idle")

    def test_invalid_current_state(self):
        """Test that providing an invalid current state defaults to the error state."""
        new_state = self.fsm_core.trigger("underwater", "stop")
        self.assertEqual(new_state, "error")

if __name__ == '__main__':
    unittest.main()
