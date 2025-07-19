import logging
import os
from datetime import datetime
from core.file_paths import FSM_LOG_FILE

os.makedirs(os.path.dirname(FSM_LOG_FILE), exist_ok=True)

logger = logging.getLogger("fsm_logger")
if not logger.handlers:
    handler = logging.FileHandler(FSM_LOG_FILE)
    formatter = logging.Formatter("%(asctime)s - %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)

def log_transition(from_state: dict, to_state: dict, trigger: str | None, source: str | None):
    """Log FSM transition details."""
    logger.info(
        f"{from_state.get('mode')} -> {to_state.get('mode')} | trigger={trigger} | source={source} | value={to_state}"
    )
