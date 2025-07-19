import json
import os
import time
from datetime import datetime
import sys

# Add project root to sys.path for imports
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
sys.path.append(project_root)

from qiki_bot.core.file_paths import SHARED_BUS_FILE
from qiki_bot.core.localization_manager import LocalizationManager

# Initialize localization
loc = LocalizationManager()

# ANSI color codes
COLOR_RED = "\033[91m"
COLOR_GREEN = "\033[92m"
COLOR_YELLOW = "\033[93m"
COLOR_BLUE = "\033[94m"
COLOR_RESET = "\033[0m"

# --- HELPER FUNCTIONS (can be used later for data integration) ---

def clear_screen():
    """Clears the terminal screen."""
    # Using ANSI escape code for broader compatibility
    print("\033[H\033[J", end="")

def read_shared_bus() -> dict:
    """Safely reads the shared_bus.json file."""
    if not os.path.exists(SHARED_BUS_FILE):
        return {"error": f"⚠️  {os.path.basename(SHARED_BUS_FILE)} not found"}
    try:
        with open(SHARED_BUS_FILE, 'r') as f:
            content = f.read()
            if not content.strip():
                return {"error": f"⚠️  {os.path.basename(SHARED_BUS_FILE)} is empty"}
            data = json.loads(content)
            return data
    except (json.JSONDecodeError, IOError) as e:
        return {"error": f"⚠️  Error reading {os.path.basename(SHARED_BUS_FILE)}: {e}"}

# --- NEW TERMINAL DASHBOARD ---

def render_terminal_dashboard():
    """
    Renders the QIKI Terminal Cockpit v3.0.
    This function contains the hardcoded ASCII layout.
    """
    clear_screen()
    # Data can be dynamically injected here in the future.
    # For now, it's a static template.
    dashboard_output = f"""
╔═════════════════ {loc.get_dual('cockpit_header')} ═════════════════╗
║                                                                  ║
║  {loc.get_dual('cockpit_power_systems_header')}                                   ║
║  ├─ {loc.get_dual('cockpit_power_main_battery')}:     [░░░░░░░░░░] 0%          ║
║  ├─ {loc.get_dual('cockpit_power_solar_array')}:     [░░░░░░░░░░] 0%          ║
║  ├─ {loc.get_dual('cockpit_power_consumption')}:          [░░░░░░░░░░] 0%          ║
║  ╰─ {loc.get_dual('cockpit_power_est_runtime')}:     [0.0 ч] [{loc.get_dual('cockpit_power_runtime_variable')}]     ║
║                                                                  ║
║  {loc.get_dual('cockpit_compute_header')}                                ║
║  ├─ {loc.get_dual('cockpit_compute_q_core')}:                   [░░░░░░░░░░] 0%           ║
║  ├─ {loc.get_dual('cockpit_compute_e_core')}:                   [░░░░░░░░░░] 0%           ║
║  ├─ {loc.get_dual('cockpit_compute_p_core')}:                   [░░░░░░░░░░] 0%           ║
║  ├─ {loc.get_dual('cockpit_compute_m_core')}:                   [░░░░░░░░░░] 0%           ║
║  ╰─ {loc.get_dual('cockpit_compute_r_core')}:                   [{loc.get_dual('cockpit_compute_r_core_status')}]      ║
║                                                                  ║
║  {loc.get_dual('cockpit_memory_header')}                                           ║
║  ├─ {loc.get_dual('cockpit_memory_ram')}:                      [░░░░░░░░░░] 0%              ║
║  ╰─ {loc.get_dual('cockpit_memory_storage')}:           [░░░░░░░░░░] 0%              ║
║                                                                  ║
║  {loc.get_dual('cockpit_temp_header')}                                       ║
║  ├─ {loc.get_dual('cockpit_temp_core')}:        [░░░░░░░░░░] 0°C             ║
║  ├─ {loc.get_dual('cockpit_temp_propulsion')}:        [░░░░░░░░░░] 0°C             ║
║  ╰─ {loc.get_dual('cockpit_temp_external')}:      [░░░░░░░░░░] 0°C             ║
║                                                                  ║
║  {loc.get_dual('cockpit_integrity_header')}                                         ║
║  ├─ {loc.get_dual('cockpit_integrity_hull')}:              [░░░░░░░░░░] 0%                ║
║  ├─ {loc.get_dual('cockpit_integrity_shielding')}:           [░░░░░░░░░░] 0%                ║
║  ╰─ {loc.get_dual('cockpit_integrity_components')}:      [░░░░░░░░░░] 0%                ║
║                                                                  ║
╚══════════════════════════════════════════════════════════════════╝
"""
    print(dashboard_output)
    print(f"{loc.get('cockpit_last_refresh')}: {datetime.now().strftime('%H:%M:%S')} | {loc.get('cockpit_exit_prompt')}")


# --- MAIN EXECUTION LOOP ---

def run_monitor():
    """
    Main loop to continuously render the dashboard.
    """
    print(loc.get('cockpit_initializing'))
    time.sleep(1)
    while True:
        try:
            # In the future, data fetching would happen here
            render_terminal_dashboard()
            time.sleep(2) # Refresh every 2 seconds
        except KeyboardInterrupt:
            clear_screen()
            print(loc.get('cockpit_terminated'))
            break

if __name__ == "__main__":
    run_monitor()
    print(loc.get("cockpit_log_localized_successfully"))