import os
import json
import time
import logging
import datetime
import fcntl

from core.fsm_interface import FSMInterface
from core.file_paths import FSM_REQUESTS_FILE, FSM_LOG_FILE, FSM_STATE_FILE, BASE_DIR

# --- Logging Setup ---
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] [%(levelname)s] [GATEKEEPER] %(message)s',
    handlers=[
        logging.FileHandler(FSM_LOG_FILE),
        logging.StreamHandler()
    ]
)
log = logging.getLogger(__name__)

# --- Banner ---
def banner(title: str, description: str):
    log.info("=" * 80)
    log.info(f"  МОДУЛЬ: {title}")
    log.info(f"  Назначение: {description}")
    log.info(f"  Время запуска: {datetime.datetime.now().isoformat()}")
    log.info(f"  PID процесса: {os.getpid()}")
    log.info(f"  Путь: {os.path.abspath(__file__)}")
    log.info("=" * 80)

banner(
    title="FSM Gatekeeper / Хранитель Состояний",
    description="Единственный процесс, управляющий записью в fsm_state.json через FSM_IO."
)
# --- End Banner ---

def get_requests():
    """
    Safely reads and clears the request queue file.
    Returns a list of requests.
    """
    if not os.path.exists(FSM_REQUESTS_FILE):
        return []
    
    requests = []
    try:
        with open(FSM_REQUESTS_FILE, "r+") as f:
            fcntl.flock(f, fcntl.LOCK_EX | fcntl.LOCK_NB)
            try:
                content = f.read()
                if content:
                    requests = json.loads(content)
                f.seek(0)
                f.truncate()
            except (json.JSONDecodeError, IndexError):
                log.warning(f"Could not decode {FSM_REQUESTS_FILE}. Clearing file.")
                f.seek(0)
                f.truncate()
            except BlockingIOError:
                return [] # Another process holds the lock, skip this cycle.
            finally:
                fcntl.flock(f, fcntl.LOCK_UN)
    except (IOError, FileNotFoundError):
        return []
        
    return requests if isinstance(requests, list) else []


def run_gatekeeper():
    """The main loop for the FSM Gatekeeper process."""
    log.info("FSM Gatekeeper process starting.")
    
    # Initialize the FSM Interface
    fsm_interface = FSMInterface()

    log.info("Gatekeeper is now running...")
    while True:
        requests = get_requests()

        if requests:
            log.info(f"Processing {len(requests)} command(s) from queue.")
            for req in requests:
                if isinstance(req, dict) and "event" in req:
                    event = req["event"]
                    source = req.get("from", "unknown")
                    metadata = req.get("metadata") # Optional metadata
                    log.info(f"Executing event '{event}' from '{source}'.")
                    
                    # Use the FSM Interface to trigger the event
                    fsm_interface.trigger_event(event, metadata)
                else:
                    log.warning(f"Received invalid request format: {req}")
        
        time.sleep(0.2) # Prevent busy-waiting

if __name__ == "__main__":
    # Ensure the request file exists to avoid startup race conditions
    if not os.path.exists(FSM_REQUESTS_FILE):
        with open(FSM_REQUESTS_FILE, 'w') as f:
            json.dump([], f)
            
    run_gatekeeper()