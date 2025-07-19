import os
import json
import sys

# Add project root to sys.path for imports
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(project_root)

from core.file_paths import TELEMETRY_FILE, FSM_STATE_FILE, SENSORS_FILE, SHARED_BUS_FILE

# --- CONFIGURATION ---
FILES_TO_CHECK = [
    TELEMETRY_FILE,
    FSM_STATE_FILE,
    SENSORS_FILE,
    SHARED_BUS_FILE,
]

# ANSI color codes
COLOR_RED = "\033[91m"
COLOR_GREEN = "\033[92m"
COLOR_YELLOW = "\033[93m"
COLOR_RESET = "\033[0m"

# --- HELPER FUNCTIONS ---

def check_json_file(filepath: str) -> dict:
    """Checks a JSON file for existence and validity."""
    status = {"path": filepath, "exists": False, "valid_json": False, "status_msg": ""}

    if not os.path.exists(filepath):
        status["status_msg"] = f"{COLOR_YELLOW}MISSING{COLOR_RESET}"
        return status

    status["exists"] = True
    try:
        with open(filepath, 'r') as f:
            content = f.read()
            if not content.strip():
                status["status_msg"] = f"{COLOR_YELLOW}EMPTY{COLOR_RESET}"
                return status
            json.loads(content)
            status["valid_json"] = True
            status["status_msg"] = f"{COLOR_GREEN}OK{COLOR_RESET}"
    except json.JSONDecodeError as e:
        status["status_msg"] = f"{COLOR_RED}BROKEN (JSON Error: {e}){COLOR_RESET}"
    except IOError as e:
        status["status_msg"] = f"{COLOR_RED}BROKEN (IO Error: {e}){COLOR_RESET}"
    except Exception as e:
        status["status_msg"] = f"{COLOR_RED}BROKEN (Unexpected Error: {e}){COLOR_RESET}"
    
    return status

# --- MAIN EXECUTION ---

def run_diagnostics():
    print("\n--- QIKI Bot System Diagnostics / Диагностика Системы QIKI Bot ---")
    print("Checking critical JSON files...\n")

    results = []
    for file_path in FILES_TO_CHECK:
        results.append(check_json_file(file_path))

    # --- Summary Table ---
    print("╔" + "═" * 78 + "╗")
    print("║ {:<30} │ {:<40} ║".format("File / Файл", "Status / Статус"))
    print("╠" + "═" * 30 + "╧" + "═" * 40 + "╣")

    for res in results:
        file_basename = os.path.basename(res["path"])
        print("║ {:<30} │ {:<40} ║".format(file_basename, res["status_msg"]))

    print("╚" + "═" * 30 + "╧" + "═" * 40 + "╝")
    print("\nDiagnostics complete.")

if __name__ == "__main__":
    run_diagnostics()