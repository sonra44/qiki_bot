# -*- coding: utf-8 -*-
"""
QIKI Bot
FSM I/O - Enqueues FSM events.
"""
import json
import os
import fcntl
import logging
import datetime
from typing import Dict, Any, Optional

from .file_paths import FSM_REQUESTS_FILE

# Setup logging
log = logging.getLogger(__name__)

def enqueue_event(event: str, source: str, metadata: Optional[Dict[str, Any]] = None) -> None:
    """
    Atomically adds a command to the fsm_requests.json queue.
    This is the method external modules should use to request a state change.
    """
    request = {
        "event": event, 
        "from": source,
        "timestamp": datetime.datetime.now().isoformat(),
        "metadata": metadata
    }

    try:
        # Ensure the file exists before trying to lock it
        if not os.path.exists(FSM_REQUESTS_FILE):
            with open(FSM_REQUESTS_FILE, 'w') as f:
                json.dump([], f)

        with open(FSM_REQUESTS_FILE, "r+") as f:
            fcntl.flock(f, fcntl.LOCK_EX)
            try:
                queue = json.load(f)
                queue.append(request)
                f.seek(0)
                f.truncate()
                json.dump(queue, f, indent=4)
                log.info(f"Enqueued event '{event}' from '{source}'. Queue size: {len(queue)}")
            except json.JSONDecodeError:
                log.warning(f"Could not decode {FSM_REQUESTS_FILE}. Overwriting with new request.")
                json.dump([request], f, indent=4)
            finally:
                fcntl.flock(f, fcntl.LOCK_UN)
    except IOError as e:
        log.error(f"Failed to enqueue event in {FSM_REQUESTS_FILE}: {e}")