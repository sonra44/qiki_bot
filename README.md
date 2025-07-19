 QIKI Bot

QIKI Bot is a minimal multi-agent system built with pure Python and JSON. Communication between modules occurs only through local JSON files, making it easy to run even in restricted or offline environments.

## Project layout
- `core/` — state machine and shared bus utilities
- `sensors/` — sensor clusters and simulator
- `interfaces/cli/` — command-line dashboards
- `tools/` — helper scripts
- `simulation/` — simple physics engine

## File overview
- `GEMINI_CHANGELOG.md` — complete development log
- `RAW/` — raw documentation and design ideas
- `assistant.py` — interactive CLI assistant
- `config/` — configuration files and locales
- `core/` — FSM logic and agent utilities
- `event_trigger.py` — trigger FSM events from the shell
- `fsm_requests.json` — queue of pending FSM commands
- `fsm_state.json` — current FSM state
- `interfaces/` — command-line dashboards
- `logs/` — log output
- `mission_state.json` — mission data store
- `mission_status.json` — high-level mission status
- `ml/` — machine learning experiments
- `navigation_monitor.py` — navigation data monitor
- `operator_interface.py` — operator command interface
- `power_core.py` — power management logic
- `prompts/` — conversation prompts for agents
- `qiki_boot_log.json` — boot log
- `requirements.txt` — Python dependencies
- `run_all.sh` — launch all background services
- `sensor_manager_demo.py` — demo of the sensor manager
- `sensor_overlay.py` — overlay showing sensor values
- `sensors/` — sensor definitions and clusters
- `sensors.json` — latest sensor readings
- `sensors.json.lock` — lock file for sensors.json
- `shared_bus.json` — communication bus for agents
- `shared_bus.json.lock` — lock for shared_bus.json
- `simulation/` — simple physics simulation
- `start.sh` — convenience start script
- `state_monitor.py` — terminal FSM state display
- `status_hud.py` — heads-up display for system status
- `system_diagnostics.py` — diagnostic collector
- `task_state.json` — task tracking file
- `telemetry.json` — telemetry data
- `telemetry.json.lock` — lock for telemetry.json
- `tests/` — unit tests
- `tools/` — helper utilities
- `voice_logger.py` — speech log generator
## Quick start
1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Launch background services:
   ```bash
   bash run_all.sh
   ```
3. Optional: start the 3D world demo:
   ```bash
   bash run_world.sh
   ```

## Tests
Run all tests with:
```bash
pytest -q
```

### 🔁 Cached RuleEngine

- `rules.json` больше не перечитывается каждый тик
- Все правила загружаются один раз в `RuleEngine.__init__()`
- Метод `reload_rules()` позволяет перезагрузить их вручную
- Повышает производительность симуляции на ~50% при 10+ правилах

## Русская версия

**QIKI Bot — система из нескольких агентов на чистом Python.** Все модули обмениваются данными через локальные JSON-файлы, что позволяет запускать проект в ограниченных средах.

### Структура проекта
- `core/` — машина состояний и общая шина
- `sensors/` — кластеры сенсоров и симулятор
- `interfaces/cli/` — панели командной строки
- `tools/` — вспомогательные скрипты
- `simulation/` — пример физического движка

### Обзор файлов
- `GEMINI_CHANGELOG.md` — подробный журнал изменений
- `RAW/` — черновые документы и идеи
- `assistant.py` — интерактивный помощник в терминале
- `config/` — конфигурация и локализация
- `core/` — логика FSM и утилиты агентов
- `event_trigger.py` — отправка событий в FSM
- `fsm_requests.json` — очередь команд FSM
- `fsm_state.json` — текущее состояние FSM
- `interfaces/` — интерфейсы командной строки
- `logs/` — файлы журналов
- `mission_state.json` — данные миссий
- `mission_status.json` — статус миссии
- `ml/` — эксперименты с ML
- `navigation_monitor.py` — монитор навигации
- `operator_interface.py` — интерфейс оператора
- `power_core.py` — логика энергосистемы
- `prompts/` — подсказки для моделей
- `qiki_boot_log.json` — лог загрузки
- `requirements.txt` — зависимости Python
- `run_all.sh` — запуск всех модулей
- `sensor_manager_demo.py` — демонстрация менеджера сенсоров
- `sensor_overlay.py` — наложение данных сенсоров
- `sensors/` — реализация сенсоров
- `sensors.json` — текущие данные сенсоров
- `sensors.json.lock` — блокировка sensors.json
- `shared_bus.json` — общая шина обмена
- `shared_bus.json.lock` — блокировка шины
- `simulation/` — физический симулятор
- `start.sh` — простой скрипт запуска
- `state_monitor.py` — вывод состояния FSM
- `status_hud.py` — HUD системного статуса
- `system_diagnostics.py` — сбор диагностики
- `task_state.json` — состояние задач
- `telemetry.json` — телеметрия
- `telemetry.json.lock` — блокировка телеметрии
- `tests/` — тесты
- `tools/` — утилиты
- `voice_logger.py` — ведение голосового лога
### Быстрый старт
1. Установите зависимости:
   ```bash
   pip install -r requirements.txt
   ```
2. Запустите процессы:
   ```bash
   bash run_all.sh
   ```
3. При желании запустите 3D-мир:
   ```bash
   bash run_world.sh
   ```

### Тесты
Для запуска тестов выполните:
```bash
pytest -q
```
