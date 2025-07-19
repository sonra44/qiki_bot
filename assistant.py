import os
import sys
from core.localization_manager import loc
from core.fsm_client import FSMClient  # Use the client to send requests

class Assistant:
    def __init__(self):
        self.fsm_client = FSMClient()
        print(f"--- {loc.get_dual('assistant_title')} ---")
        print(loc.get_dual('enter_command'))

    def _display_help(self):
        print(f"\n--- {loc.get_dual('help_title')} ---")
        print(f"  fsm <event> - {loc.get_dual('fsm_command')}")
        print(f"  clear       - {loc.get_dual('clear_command')}")
        print(f"  exit        - {loc.get_dual('exit_command')}")
        print("--- End ---\n")

    def _process_command(self, command_line: str):
        cmd_parts = command_line.lower().split(maxsplit=1)
        main_cmd = cmd_parts[0]

        if main_cmd == "fsm":
            if len(cmd_parts) > 1:
                event = cmd_parts[1]
                print(f"Sending event: {event}")
                self.fsm_client.send_event(event, source='assistant')
            else:
                print(f"Usage: fsm <event>")
        elif main_cmd in ["h", "help"]:
            self._display_help()
        elif main_cmd == "clear":
            os.system('cls' if os.name == 'nt' else 'clear')
        elif main_cmd == "exit":
            return False  # Signal to quit
        else:
            print(f"Unknown command: '{command_line}'")
        return True

    def run(self):
        while True:
            try:
                command = input("> ").strip()
                if not command:
                    continue
                if not self._process_command(command):
                    break
            except (EOFError, KeyboardInterrupt):
                print("\nExiting...")
                break
            except Exception as e:
                print(f"[ERROR] {e}")

        print("Assistant terminated.")

if __name__ == "__main__":
    # Add project root to sys.path for imports
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    if project_root not in sys.path:
        sys.path.append(project_root)
    
    assistant = Assistant()
    assistant.run()

