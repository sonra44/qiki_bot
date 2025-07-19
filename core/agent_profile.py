import os
import json
from datetime import datetime

# Путь к shared_bus.json
# Предполагается, что shared_bus.json находится в корне qiki_bot
SHARED_BUS_FILE = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'shared_bus.json'))

class AgentProfileManager:
    def __init__(self):
        self.agents = self._load()
        print(f"[AgentProfileManager] Инициализирован. Загружено {len(self.agents)} агентов.")

    def _load(self):
        """Загружает JSON из shared_bus.json. При ошибке инициализирует пустой словарь."""
        if not os.path.exists(SHARED_BUS_FILE):
            print(f"[WARN] {SHARED_BUS_FILE} не найден. Инициализация пустым словарем.")
            return {}
        try:
            with open(SHARED_BUS_FILE, 'r') as f:
                content = f.read()
                if not content.strip():
                    print(f"[WARN] {SHARED_BUS_FILE} пуст. Инициализация пустым словарем.")
                    return {}
                data = json.loads(content)
                if not isinstance(data, dict):
                    print(f"[WARN] {SHARED_BUS_FILE} содержит некорректный формат. Ожидается словарь. Инициализация пустым словарем.")
                    return {}
                print(f"[INFO] Успешно загружено {len(data)} агентов из {SHARED_BUS_FILE}.")
                return data
        except (json.JSONDecodeError, IOError) as e:
            print(f"[WARN] {SHARED_BUS_FILE} повреждён или ошибка чтения: {e}. Инициализация пустым словарем.")
            return {}

    def _save(self):
        """Сохраняет текущее состояние агентов в shared_bus.json."""
        try:
            with open(SHARED_BUS_FILE, 'w') as f:
                json.dump(self.agents, f, indent=2)
            print(f"[INFO] Успешно сохранено {len(self.agents)} агентов в {SHARED_BUS_FILE}.")
        except IOError as e:
            print(f"[ERROR] Не удалось сохранить {SHARED_BUS_FILE}: {e}")

    def register(self, agent_id: str, role: str = "default"):
        """Регистрирует нового агента с базовыми параметрами, если его нет."""
        if agent_id not in self.agents:
            self.agents[agent_id] = {
                "state": "idle",
                "last_update": self._now(),
                "battery": 100.0,
                "position": [0.0, 0.0],
                "role": role,
                "status": "ready",
                "type": "unknown", # Добавлено для соответствия AgentProfile
                "name": agent_id, # Добавлено для соответствия AgentProfile
                "impulse_active": False # Добавлено для соответствия AgentProfile
            }
            self._save()
            print(f"[INFO] Агент '{agent_id}' зарегистрирован.")
        else:
            print(f"[INFO] Агент '{agent_id}' уже зарегистрирован.")

    def update(self, agent_id: str, **kwargs):
        """Обновляет данные существующего агента. Регистрирует, если агента нет."""
        if agent_id not in self.agents:
            self.register(agent_id) # Автоматическая регистрация, если агент не найден
            print(f"[INFO] Агент '{agent_id}' не найден, зарегистрирован перед обновлением.")

        for k, v in kwargs.items():
            self.agents[agent_id][k] = v
        self.agents[agent_id]["last_update"] = self._now()
        self._save()
        print(f"[INFO] Агент '{agent_id}' обновлен: {kwargs}.")

    def get(self, agent_id: str) -> dict | None:
        """Возвращает словарь данных агента по ID, или None если не найден."""
        agent_data = self.agents.get(agent_id, None)
        if agent_data:
            print(f"[INFO] Получены данные агента '{agent_id}'.")
        else:
            print(f"[INFO] Агент '{agent_id}' не найден.")
        return agent_data

    def remove(self, agent_id: str):
        """Удаляет агента по ID."""
        if agent_id in self.agents:
            del self.agents[agent_id]
            self._save()
            print(f"[INFO] Агент '{agent_id}' удален.")
        else:
            print(f"[WARN] Агент '{agent_id}' не найден для удаления.")

    def list_all(self) -> dict:
        """Возвращает словарь всех агентов."""
        print(f"[INFO] Возвращен список из {len(self.agents)} агентов.")
        return self.agents

    def _now(self) -> str:
        """Возвращает текущее время в формате ISO 8601 UTC."""
        return datetime.utcnow().isoformat(timespec='seconds')

# Пример запуска
if __name__ == "__main__":
    print("--- Тест AgentProfileManager ---")

    # Очистка файла для чистого теста
    if os.path.exists(SHARED_BUS_FILE):
        os.remove(SHARED_BUS_FILE)
        print(f"[INFO] Удален существующий {SHARED_BUS_FILE} для теста.")

    manager = AgentProfileManager()

    # Регистрация и обновление агентов
    manager.register("agent_001", role="scout")
    manager.update("agent_001", battery=91.5, state="active", position=[10.0, 5.2])

    manager.register("agent_002", role="commander")
    manager.update("agent_002", battery=100.0, state="idle", position=[0.0, 0.0])

    print("\n--- Текущие данные агентов ---")
    for agent_id, data in manager.list_all().items():
        print(f"Агент ID: {agent_id}, Данные: {data}")

    # Получение конкретного агента
    agent1_data = manager.get("agent_001")
    if agent1_data:
        print(f"\nПолучен агент_001: {agent1_data}")

    # Обновление существующего агента
    manager.update("agent_001", state="charging", battery=95.0)
    print(f"\nОбновлен агент_001: {manager.get('agent_001')}")

    # Удаление агента
    manager.remove("agent_002")
    print("\n--- Агенты после удаления agent_002 ---")
    print(manager.list_all())

    # Тест загрузки из файла после операций
    print("\n--- Тест перезагрузки менеджера ---")
    new_manager = AgentProfileManager()
    print("Агенты, загруженные новым менеджером:")
    print(new_manager.list_all())

    print("--- Тест AgentProfileManager завершен ---")