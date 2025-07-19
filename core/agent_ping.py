import os
import time
import json
import random
from datetime import datetime
from core.shared_bus_manager import SharedBusManager # Import SharedBusManager

# --- CONFIGURATION ---
AGENT_ID = "agent_001"
# SHARED_BUS_FILE is now managed by SharedBusManager

# --- HELPER FUNCTIONS ---
def simulate_agent_state() -> dict:
    """Генерирует случайное состояние агента."""
    battery = round(random.uniform(10.0, 100.0), 2)
    state = "active" if battery > 20 else "low_power"
    status = "OK" if battery > 20 else "LOW_POWER"
    position = [round(random.uniform(0, 9), 1), round(random.uniform(0, 9), 1)]
    timestamp = datetime.utcnow().isoformat(timespec='seconds')
    
    return {
        "role": "scanner",
        "state": state,
        "status": status,
        "battery": battery,
        "position": position,
        "last_update": timestamp,
        "last_heartbeat": datetime.utcnow().isoformat(timespec='seconds') + 'Z' # UTC ISO 8601 with Z for Zulu time
    }

# --- MAIN EXECUTION LOOP ---
def run_ping_loop():
    print(f"[INFO] Агент {AGENT_ID} начал пинговать...")
    shared_bus_manager = SharedBusManager() # Instantiate SharedBusManager

    while True:
        # Use SharedBusManager to load and update agent data
        agent_data = simulate_agent_state()
        shared_bus_manager.update_agent(AGENT_ID, agent_data)
        
        print(f"[PING] Обновление агента {AGENT_ID} в shared_bus.json — battery: {agent_data['battery']}% | position: {agent_data['position']}")
        time.sleep(2)

if __name__ == "__main__":
    try:
        run_ping_loop()
    except KeyboardInterrupt:
        print("\n[INFO] Завершено вручную.")