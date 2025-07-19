import os
import time
from datetime import datetime
import sys

# Add project root to sys.path for imports
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(project_root)

from core.fsm_client import FSMClient

# --- CONFIGURATION ---
POLLING_INTERVAL = 1.5 # seconds

# --- GLOBAL STATE ---
LAST_FSM_STATE = None

# --- MAIN EXECUTION LOOP ---

def run_voice_logger():
    global LAST_FSM_STATE
    fsm_client = FSMClient()

    print("Starting Voice Logger. Monitoring FSM state changes. Press Ctrl+C to exit.")

    # Initial read to set LAST_FSM_STATE
    initial_state_data = fsm_client.get_state()
    LAST_FSM_STATE = initial_state_data.get("mode", "UNKNOWN")
    print(f"[INFO] Initial FSM state: {LAST_FSM_STATE}")

    try:
        while True:
            current_state_data = fsm_client.get_state()
            current_fsm_state = current_state_data.get("mode", "error")

            if current_fsm_state != LAST_FSM_STATE:
                timestamp = datetime.now().strftime("%H:%M:%S")
                print(f"️[{timestamp}] Состояние изменено: {current_fsm_state.upper()}")
                LAST_FSM_STATE = current_fsm_state
            
            time.sleep(POLLING_INTERVAL)

    except KeyboardInterrupt:
        print("\nVoice Logger terminated by user.")
    except Exception as e:
        print(f"[CRITICAL ERROR] An unexpected error occurred in Voice Logger: {e}")

if __name__ == "__main__":
    run_voice_logger()
