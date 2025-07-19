import os
import time
import random
import logging
from datetime import datetime
from core.shared_bus_manager import SharedBusManager  # Import SharedBusManager

# --- CONFIGURATION ---
# SHARED_BUS_FILE is now managed by SharedBusManager
LOG_FILE = os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..', 'logs', 'comm_link.log')
)
UPDATE_INTERVAL = 3  # seconds

# --- LOGGING SETUP ---
os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)

# --- HELPER FUNCTIONS ---

def simulate_comm_link() -> dict:
    """Simulates communication link parameters and determines status."""
    latency = round(random.uniform(20, 300), 1)
    rssi = round(random.uniform(-90, -50), 1)

    if latency > 250:
        status = "timeout"
    elif latency > 100 or rssi < -80:
        status = "weak"
    else:
        status = "online"

    return {
        "latency_ms": latency,
        "rssi_db": rssi,
        "status": status
    }

# --- MAIN LOGIC ---

def update_comm_links():
    """
    Main function to update communication links for all agents in the shared bus.
    """
    logging.info("CommLink process started.")
    shared_bus_manager = SharedBusManager() # Instantiate SharedBusManager

    while True:
        agents = shared_bus_manager.load_bus() # Use SharedBusManager to load
        if not isinstance(agents, dict) or not agents:
            logging.warning("Shared bus is empty or invalid. Skipping update cycle.")
            time.sleep(UPDATE_INTERVAL)
            continue

        agent_ids = list(agents.keys())
        
        for agent_id in agent_ids:
            # Ensure the agent's data is a dictionary
            if not isinstance(agents.get(agent_id), dict):
                logging.warning(f"Agent '{agent_id}' data is not a dictionary. Skipping.")
                continue
            
            # Initialize 'comm' field if it doesn't exist
            if "comm" not in agents[agent_id]:
                agents[agent_id]["comm"] = {}

            for other_agent_id in agent_ids:
                if agent_id == other_agent_id:
                    continue

                # Simulate the link from agent_id to other_agent_id
                link_data = simulate_comm_link()
                agents[agent_id]["comm"][other_agent_id] = link_data
            
            # Update the last_update timestamp for the current agent
            agents[agent_id]["last_update"] = datetime.now().isoformat(timespec='seconds')

        shared_bus_manager.save_bus(agents) # Use SharedBusManager to save
        logging.info(f"CommLink updated shared_bus.json for {len(agent_ids)} agents.")
        
        time.sleep(UPDATE_INTERVAL)

if __name__ == "__main__":
    try:
        update_comm_links()
    except KeyboardInterrupt:
        logging.info("CommLink process terminated by user.")
    except Exception as e:
        logging.critical(f"A critical error occurred in CommLink: {e}", exc_info=True)
