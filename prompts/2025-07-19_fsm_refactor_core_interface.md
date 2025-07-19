
Цель: Архитектурное разделение логики FSM. Вынести бизнес-логику FSM (состояния, переходы, условия) в чистый модуль без I/O, и оставить работу с файлами и JSON — в отдельном интерфейсном модуле.

1. Создай файл: `fsm_core.py`
   - Класс: `FiniteStateMachine`
   - Хранит: текущее состояние, граф переходов, регистр состояний, события
   - Методы:
     - `.trigger_event(event: str, meta: dict)` — попытка перехода
     - `.get_current_state()` → возвращает текущее состояние
     - `.get_possible_transitions()` → список доступных переходов
     - `.load_state(state_dict: dict)` и `.export_state()` — для сериализации состояния

2. Создай файл: `fsm_interface.py`
   - Работает с JSON (через shared_json_cache.py)
   - Следит за `fsm_state.json`, `mission_file.json`
   - Обновляет состояние FSM, вызывает `trigger_event(...)`
   - Логирует все события через system_logger
   - Поддерживает CLI-команды: `fsm status`, `fsm trigger <EVENT>`

3. Убери I/O из старого `fsm.py`
   - Оставь только вызовы FSM Core и интерфейса
   - FSM теперь должен быть plug-and-play: можно подменить конфигурацию, заменить ядро и переиспользовать

4. Добавь базовый конфиг переходов:
   - Словарь `TRANSITIONS = { "IDLE": {"CHARGE": "CHARGING", ... }, ... }`
   - Поддержи гибкую схему с загрузкой переходов из mission-файла (в перспективе)

5. CLI Debug Tool:
   - Добавь `tools/fsm_debugger.py`
     - Команды: `status`, `step`, `list`, `inject_event`, `force_state`
     - Выводит трассировку переходов, текущее состояние, историю
