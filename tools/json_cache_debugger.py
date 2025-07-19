
import sys
import os
import time

# Add project root to sys.path to allow imports from core
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

from core.shared_json_cache import json_cache, CACHED_FILES

def print_header():
    print("="*50)
    print(" QIKI Bot - JSON Cache Debugger")
    print("="*50)
    print("Commands: list, get <path>, refresh <path>, flush, exit")
    print("Example: get telemetry.json")
    print("-"*50)

def main():
    print_header()
    
    # Start the background watcher so the cache is live
    json_cache.start_cache_watcher()
    print("Cache watcher started in the background.")

    try:
        while True:
            cmd_input = input("> ").strip().lower().split()
            if not cmd_input:
                continue

            command = cmd_input[0]

            if command == "exit":
                print("Exiting debugger.")
                break
            
            elif command == "list":
                print("Files currently managed by the cache:")
                for path in CACHED_FILES:
                    print(f" - {os.path.basename(path)}")
            
            elif command == "get":
                if len(cmd_input) > 1:
                    file_key = cmd_input[1]
                    # Find the full path from the basename
                    target_path = next((p for p in CACHED_FILES if os.path.basename(p) == file_key), None)
                    if target_path:
                        data = json_cache.get_json(target_path)
                        print(f"--- Cache content for {file_key} ---")
                        import json
                        print(json.dumps(data, indent=2))
                        print("-------------------------------------")
                    else:
                        print(f"Error: File '{file_key}' is not managed by the cache.")
                else:
                    print("Usage: get <filename>")

            elif command == "refresh":
                if len(cmd_input) > 1:
                    file_key = cmd_input[1]
                    target_path = next((p for p in CACHED_FILES if os.path.basename(p) == file_key), None)
                    if target_path:
                        print(f"Forcing refresh for {file_key}...")
                        json_cache.refresh(target_path)
                        print("Refresh complete.")
                    else:
                        print(f"Error: File '{file_key}' is not managed by the cache.")
                else:
                    print("Usage: refresh <filename>")

            elif command == "flush":
                print("Flushing cache is not directly supported as it's managed by the watcher.")
                print("To reload all, restart the debugger.")

            else:
                print(f"Unknown command: '{command}'")

    except KeyboardInterrupt:
        print("\nExiting debugger.")
    finally:
        # Stop the watcher thread gracefully
        json_cache.stop_cache_watcher()

if __name__ == "__main__":
    main()
