from datetime import datetime
from core.shared_bus_manager import SharedBusManager

class AgentComm:
    def __init__(self, agent_id: str):
        self.agent_id = agent_id
        self.bus = SharedBusManager()

    def heartbeat(self):
        data = {
            "last_heartbeat": datetime.utcnow().isoformat() + "Z",
            "status": "ALIVE",
        }
        self.bus.update_agent(self.agent_id, data)
