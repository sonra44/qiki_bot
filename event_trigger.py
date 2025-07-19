import json
import os
import sys

# Add project root to sys.path for imports
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(project_root)

from core.file_paths import FSM_STATE_FILE
from core.fsm_client import send_event

# --- CONFIGURATION ---
AVAILABLE_EVENTS = ["start_move", "stop", "charge", "error", "reset"]

# --- HELPER FUNCTIONS ---

def clear_screen():
    """Clears the terminal screen."""
    os.system('cls' if os.name == 'nt' else 'clear')

def get_current_fsm_state() -> str:
    """Reads the current FSM state from the file."""
    if not os.path.exists(FSM_STATE_FILE):
        return "FILE_MISSING"
    try:
        with open(FSM_STATE_FILE, 'r') as f:
            content = f.read()
            if not content.strip():
                return "FILE_EMPTY"
            data = json.loads(content)
            return data.get("state", "UNKNOWN")
    except (json.JSONDecodeError, IOError) as e:
        return f"ERROR: {e}"

# --- MAIN EXECUTION ---

def run_event_trigger():

    print("--- QIKI Bot FSM Event Trigger / Запуск Событий FSM ---")
    print("Type 'quit' to exit.\n")

    while True:
        clear_screen()
        current_state = get_current_fsm_state()
        print(f"Current FSM State / Текущее состояние FSM: {current_state.upper()}\n")

        print("Available Events / Доступные события:")
        for i, event in enumerate(AVAILABLE_EVENTS):
            print(f"  {i+1}. {event}")
        print("\n")

        choice = input("Enter event number or name (or 'quit'): ").strip().lower()

        if choice == "quit":
            break

        event_to_trigger = None
        try:
            # Try to convert choice to an integer index
            idx = int(choice) - 1
            if 0 <= idx < len(AVAILABLE_EVENTS):
                event_to_trigger = AVAILABLE_EVENTS[idx]
        except ValueError:
            # If not an integer, treat as event name
            if choice in AVAILABLE_EVENTS:
                event_to_trigger = choice
        
        if event_to_trigger:
            print(f"Attempting to trigger '{event_to_trigger}'...")
            send_event(event_to_trigger, "event_trigger")
            # Read the state again after sending event, as it's updated by fsm_gatekeeper
            new_fsm_state = get_current_fsm_state()
            print(f"New FSM State / Новое состояние FSM: {new_fsm_state.upper()}\n")
            input("Press Enter to continue...") # Pause for user to read
        else:
            print(f"Invalid choice: '{choice}'. Please enter a valid event number or name.")
            input("Press Enter to continue...") # Pause for user to read

    clear_screen()
    print("Event Trigger terminated.")

if __name__ == "__main__":
    run_event_trigger()