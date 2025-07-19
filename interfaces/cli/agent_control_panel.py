# qiki_bot/interfaces/cli/agent_control_panel.py
import os
import json
import time
AGENT_ID = "agent_001"
SHARED_BUS_FILE = os.path.join(os.path.dirname(__file__), '..', '..', 'shared_bus.json')
def load_shared_bus():
    if not os.path.exists(SHARED_BUS_FILE):
        return {}
    try:
        with open(SHARED_BUS_FILE, 'r') as f:
            return json.load(f)
    except json.JSONDecodeError:
        return {}
def save_shared_bus(data):
    try:
        with open(SHARED_BUS_FILE, 'w') as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        print(f"[ERROR] Failed to write shared_bus.json: {e}")
def display_agent(data):
    os.system('clear')
    print(f"=== AGENT CONTROL PANEL [{AGENT_ID}] ===")
    agent = data.get(AGENT_ID)
    if not agent:
        print("⚠️ Агент не найден.")
        return
    print(f"Роль (Role): {agent.get('role')}")
    print(f"Состояние (State): {agent.get('state')}")
    print(f"Статус: {agent.get('status')}")
    print(f"Батарея: {agent.get('battery')}")%
    print(f"Позиция: {agent.get('position')}")
    print(f"Обновлено: {agent.get('last_update')}")
    print("\nКоманды:")
    print(" [1] Изменить роль")
    print(" [2] Изменить состояние")
    print(" [3] Задать батарею")
    print(" [4] Задать позицию")
    print(" [D] Диагностика")
    print(" [R] Обновить")
    print(" [Q] Выйти")
def run_panel():
    while True:
        data = load_shared_bus()
        display_agent(data)
        choice = input("\n> ").strip().upper()
        agent = data.get(AGENT_ID, {})
        if choice == "1":
            role = input("Введите новую роль: ")
            agent["role"] = role
        elif choice == "2":
            state = input("Введите новое состояние: ")
            agent["state"] = state
        elif choice == "3":
            battery = float(input("Введите уровень батареи (%): "))
            agent["battery"] = round(battery, 2)
        elif choice == "4":
            x = float(input("X: "))
            y = float(input("Y: "))
            agent["position"] = [x, y]
        elif choice == "D":
            print(" Диагностика...")
            if agent.get("battery", 0) < 15:
                print("⚠️ Низкий заряд")
            else:
                print("✅ Всё в норме.")
            time.sleep(2)
        elif choice == "Q":
            print("Выход...")
            break
        elif choice == "R":
            pass  # просто обновление
        else:
            print("Неизвестная команда.")
            time.sleep(1)
            continue
        data[AGENT_ID] = agent
        save_shared_bus(data)
if __name__ == "__main__":
    run_panel()
