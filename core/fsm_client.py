# -*- coding: utf-8 -*-
"""
QIKI Bot
FSM Client - Centralized and safe access to the bot's Finite State Machine.
All reads and writes to fsm_state.json MUST go through this client.
"""
import json
import os
import fcntl
import logging
import time
from typing import Dict, Any, Optional
from core.fsm_logger import log_transition

# --- Constants ---
FSM_STATE_FILE = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'fsm_state.json'))
LOG_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'logs'))
FSM_ERROR_LOG_FILE = os.path.join(LOG_DIR, 'fsm_errors.log')

# --- FSM Schema ---
# Defines the required fields for a valid FSM state object.
FSM_SCHEMA = {
    "mode": str,
    "task": str,
    "status": str,
    "last_event": str,
    "timestamp": float,
    "source": str,
    "context": dict
}

# --- Logger Setup ---
def setup_logger(name, log_file, level=logging.INFO):
    """Function to setup as many loggers as you want"""
    if not os.path.exists(LOG_DIR):
        os.makedirs(LOG_DIR)
        
    handler = logging.FileHandler(log_file)        
    handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
    
    logger = logging.getLogger(name)
    logger.setLevel(level)
    if not logger.handlers:
        logger.addHandler(handler)
    
    return logger

fsm_error_logger = setup_logger('fsm_error_logger', FSM_ERROR_LOG_FILE)


class FSMClient:
    """
    Provides a thread-safe and validated interface for interacting with fsm_state.json.
    """
    def __init__(self):
        # Ensure the state file exists on initialization
        if not os.path.exists(FSM_STATE_FILE):
            self._initialize_state_file()

    def _initialize_state_file(self):
        """Creates a default FSM state file if it doesn't exist."""
        initial_state = {
            "mode": "idle",
            "task": "none",
            "status": "initialized",
            "last_event": "init",
            "timestamp": time.time(),
            "source": "FSMClient",
            "context": {}
        }
        try:
            with open(FSM_STATE_FILE, 'w') as f:
                fcntl.flock(f, fcntl.LOCK_EX)
                json.dump(initial_state, f, indent=2)
                fcntl.flock(f, fcntl.LOCK_UN)
            fsm_logger.info("Initialized FSM state file.")
        except IOError as e:
            fsm_error_logger.critical(f"Failed to initialize FSM state file: {e}")
            raise

    def _validate_state(self, state_obj: Dict[str, Any]) -> bool:
        """
        Validates a state object against the FSM_SCHEMA.
        Logs errors to fsm_errors.log.
        """
        missing_keys = [key for key in FSM_SCHEMA if key not in state_obj]
        if missing_keys:
            fsm_error_logger.error(f"State validation failed. Missing keys: {missing_keys}. State: {state_obj}")
            return False
        
        type_errors = [
            f"Key '{key}' has type {type(state_obj[key]).__name__}, expected {FSM_SCHEMA[key].__name__}"
            for key in FSM_SCHEMA if not isinstance(state_obj.get(key), FSM_SCHEMA[key])
        ]
        if type_errors:
            fsm_error_logger.error(f"State validation failed. Type mismatch: {', '.join(type_errors)}. State: {state_obj}")
            return False
            
        return True

    def get_state(self) -> Dict[str, Any]:
        """
        Safely reads and returns the current FSM state from the JSON file.
        Uses a shared lock for concurrent reads.
        """
        try:
            with open(FSM_STATE_FILE, 'r') as f:
                fcntl.flock(f, fcntl.LOCK_SH)
                try:
                    state_data = json.load(f)
                except json.JSONDecodeError:
                    fsm_error_logger.error(f"Could not decode JSON from {FSM_STATE_FILE}. Returning error state.")
                    state_data = {"state": "error", "reason": "json_decode_error"}
                finally:
                    fcntl.flock(f, fcntl.LOCK_UN)
            return state_data
        except IOError as e:
            fsm_error_logger.error(f"Failed to read {FSM_STATE_FILE}: {e}. Returning error state.")
            return {"state": "error", "reason": "io_error"}

    def set_state(self, state_obj: Dict[str, Any], *, trigger: Optional[str] = None, source: Optional[str] = None) -> bool:
        """
        Validates and safely writes a new state to the FSM file.
        Uses an exclusive lock to prevent race conditions.
        
        Args:
            state_obj: The new state dictionary to write.
            trigger: The event or reason for the state change.
            source: The module or component requesting the change.

        Returns:
            True if the state was set successfully, False otherwise.
        """
        # 1. Add metadata
        state_obj['timestamp'] = time.time()
        if source:
            state_obj['source'] = source
        if trigger:
            state_obj['last_event'] = trigger

        # 2. Validate the complete object
        if not self._validate_state(state_obj):
            return False

        # 3. Get current state for logging
        current_state = self.get_state()
        from_state_summary = f"mode={current_state.get('mode')}, task={current_state.get('task')}, status={current_state.get('status')}"
        to_state_summary = f"mode={state_obj.get('mode')}, task={state_obj.get('task')}, status={state_obj.get('status')}"

        # 4. Write to file with exclusive lock
        try:
            with open(FSM_STATE_FILE, 'w') as f:
                fcntl.flock(f, fcntl.LOCK_EX)
                json.dump(state_obj, f, indent=2)
                fcntl.flock(f, fcntl.LOCK_UN)
            
            # 5. Log the successful transition
            log_transition(current_state, state_obj, trigger, source)
            return True
        except IOError as e:
            fsm_error_logger.error(f"Failed to write state to {FSM_STATE_FILE}, requested by '{source}': {e}")
            return False