import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

TELEMETRY_FILE = os.path.join(BASE_DIR, "telemetry.json")
SENSORS_FILE = os.path.join(BASE_DIR, "sensors.json")
FSM_STATE_FILE = os.path.join(BASE_DIR, "fsm_state.json")
SHARED_BUS_FILE = os.path.join(BASE_DIR, "shared_bus.json")
CONFIG_FILE = os.path.join(BASE_DIR, "config", "config.json")
RULES_FILE = os.path.join(BASE_DIR, "config", "rules.json")
FSM_REQUESTS_FILE = os.path.join(BASE_DIR, "fsm_requests.json")
FSM_LOG_FILE = os.path.join(BASE_DIR, "logs", "fsm_log.txt")
MISSION_FILE = os.path.join(BASE_DIR, "config", "mission.json")
MISSION_STATUS_FILE = os.path.join(BASE_DIR, "mission_status.json")
QIKI_BOOT_LOG_FILE = os.path.join(BASE_DIR, "qiki_boot_log.json")
LOCALES_FILE = os.path.join(BASE_DIR, "config", "locales.json")
SENSOR_LOG_FILE = os.path.join(BASE_DIR, "logs", "sensor_log.txt")
