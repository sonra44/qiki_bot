import time
import json
import os
import sys

# Add project root to sys.path for imports
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(project_root)

from core.file_paths import TELEMETRY_FILE, SENSORS_FILE, FSM_STATE_FILE, SHARED_BUS_FILE
from core.shared_bus_manager import SharedBusManager # Import SharedBusManager

FILES = [
    (TELEMETRY_FILE, " Telemetry / Телеметрия"),
    (SENSORS_FILE, " Sensors / Сенсоры"),
    (FSM_STATE_FILE, " FSM / Состояние FSM"),
    # SHARED_BUS_FILE will be handled separately via SharedBusManager
]

def read_file(filename):
    try:
        with open(filename, "r") as f:
            content = f.read()
            if not content.strip():
                return "(empty)"
            return json.loads(content)
    except FileNotFoundError:
        return f"⚠️ File not found: {filename}"
    except json.JSONDecodeError as e:
        return f"⚠️ Corrupt JSON: {e}"
    except Exception as e:
        return f"⚠️ Read error: {e}"

def clear():
    os.system('cls' if os.name == 'nt' else 'clear')

if __name__ == "__main__":
    shared_bus_manager = SharedBusManager() # Instantiate SharedBusManager
    while True:
        clear()
        print(" QIKI JSON Monitor | Монитор JSON-файлов QIKI")
        print("=" * 90)
        for file_path, title in FILES:
            print(f"{title} ({os.path.basename(file_path)})")
            print("-" * 90)
            content = read_file(file_path)
            
            if isinstance(content, dict):
                for k, v in content.items():
                    # Handle nested dictionaries for better display
                    if isinstance(v, dict):
                        print(f"{k:<25}: ")
                        for sub_k, sub_v in v.items():
                            print(f"  {sub_k:<23}: {sub_v}")
                    else:
                        print(f"{k:<25}: {v}")
            else:
                print(content)
            print()
        
        # Handle Shared Bus separately using SharedBusManager
        print(f" Shared Bus / Общая шина ({os.path.basename(SHARED_BUS_FILE)})")
        print("-" * 90)
        agents_data = shared_bus_manager.load_bus()
        if not agents_data:
            print("  (No agents registered)")
        else:
            for agent_id, agent_info in agents_data.items():
                print(f"  Agent ID: {agent_id}")
                for k, v in agent_info.items():
                    if isinstance(v, dict):
                        print(f"    {k:<23}: ")
                        for sub_k, sub_v in v.items():
                            print(f"      {sub_k:<21}: {sub_v}")
                    else:
                        print(f"    {k:<23}: {v}")
                print()
        print()

        time.sleep(2)