# -*- coding: utf-8 -*-
"""FSM Client
Provides validated access to ``fsm_state.json`` and a helper to send events
through the gatekeeper.
"""

import json
import os
import logging
from datetime import datetime
from typing import Any, Dict, Optional

from core.file_paths import FSM_STATE_FILE
from core.fsm_logger import log_transition
from core.fsm_io import enqueue_event

# Paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOG_DIR = os.path.join(BASE_DIR, "logs")
ERROR_LOG_FILE = os.path.join(LOG_DIR, "fsm_errors.log")

# Allowed FSM states. In a real setup this could be loaded from a config file.
FSM_SCHEMA = ["IDLE", "MISSION_ACTIVE", "CHARGING", "AVOIDING", "ERROR"]


class FSMClient:
    """Central access point to the FSM state."""

    def __init__(self, path: str = FSM_STATE_FILE) -> None:
        self.path = path
        self.schema = FSM_SCHEMA
        self.state = self.load_state()

    def load_state(self) -> Dict[str, Any]:
        """Load state from disk. On failure return default state."""
        try:
            with open(self.path, "r") as f:
                return json.load(f)
        except Exception as exc:
            self.log_error(f"Failed to load state: {exc}")
            return {"state": "IDLE", "last_trigger": None, "context": {}}

    def save_state(self) -> None:
        os.makedirs(os.path.dirname(self.path), exist_ok=True)
        with open(self.path, "w") as f:
            json.dump(self.state, f, indent=2)

    def get_state(self) -> Dict[str, Any]:
        """Return the currently cached state."""
        return self.state

    def set_state(self, new_state: str, metadata: Dict[str, Any]) -> bool:
        """Validate ``new_state`` and persist it with metadata."""
        if new_state not in self.schema:
            self.log_error(f"Invalid state '{new_state}'")
            return False

        from_state = self.state.get("state", "UNKNOWN")
        self.state = {
            "state": new_state,
            "last_trigger": metadata.get("trigger"),
            "context": metadata.get("context", {}),
            "timestamp": datetime.now().isoformat(),
        }
        self.save_state()
        self.log_transition(from_state, new_state, metadata)
        return True

    # --- Logging helpers -------------------------------------------------
    def log_transition(self, from_s: str, to_s: str, meta: Dict[str, Any]) -> None:
        log_transition({"state": from_s}, {"state": to_s}, meta.get("trigger"), meta.get("source"))

    def log_error(self, msg: str) -> None:
        os.makedirs(LOG_DIR, exist_ok=True)
        with open(ERROR_LOG_FILE, "a") as f:
            f.write(f"{datetime.now().isoformat()} - {msg}\n")

    # --- Event helper ----------------------------------------------------
    def send_event(self, event: str, source: str, metadata: Optional[Dict[str, Any]] = None) -> None:
        enqueue_event(event, source, metadata)


def send_event(event: str, source: str, metadata: Optional[Dict[str, Any]] = None) -> None:
    """Convenience wrapper around :func:`enqueue_event`."""
    enqueue_event(event, source, metadata)
