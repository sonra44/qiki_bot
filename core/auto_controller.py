import time
import datetime
import os
from core.rule_engine import RuleEngine
from core.fsm_client import send_event

# --- Banner ---
def banner(title: str, description: str):
    print("=" * 80)
    print(f"  МОДУЛЬ: {title}")
    print(f"  Назначение: {description}")
    print(f"  Время запуска: {datetime.datetime.now().isoformat()}")
    print(f"  PID процесса: {os.getpid()}")
    print(f"  Путь: {os.path.abspath(__file__)}")
    print("=" * 80)
    print()

banner(
    title="Auto Controller / Автономный Контроллер",
    description="Принимает решения на основе правил и отправляет запросы на изменение состояния в FSM Gatekeeper."
)
# --- End Banner ---

def run_auto_controller():
    """The main loop for the autonomous decision-making process."""
    print("[Auto Controller] Process started.")
    engine = RuleEngine()

    while True:
        # The rule engine evaluates the current state of the world
        triggered_event = engine.run_once()

        if triggered_event:
            print(f"[Auto Controller] Rule engine triggered event: '{triggered_event}'. Sending to Gatekeeper.")
            # Send the event to the FSM Gatekeeper instead of triggering directly
            send_event(event=triggered_event, source="auto_controller")
        else:
            # This is normal, means no rules met their conditions
            print("[Auto Controller] No rules triggered this cycle.")

        # The controller sleeps for a cycle
        time.sleep(2)

if __name__ == "__main__":
    run_auto_controller()
