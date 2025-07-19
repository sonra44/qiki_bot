# QIKI Bot

QIKI Bot is a minimal multi-agent system built with pure Python and JSON. All communication between modules uses local JSON files which makes it easy to run in restricted or offline environments.

## Contents
- `core/` – state machine, rule engine and shared bus management
- `sensors/` – sensor clusters and bus simulator
- `interfaces/cli/` – command line dashboards
- `tools/` – utilities such as the agent initializer
- `simulation/` – simple physics engine used for demos

## Quick start
1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Launch all background services:
   ```bash
   bash run_all.sh
   ```
3. Optional: start the 3D terminal dashboard from the `qiki_world` module with `bash run_world.sh`.

## Running tests
Execute all unit tests with:
```bash
pytest -q
```

## Русская версия

QIKI Bot — система из нескольких агентов на чистом Python без сторонних библиотек. Обмен данными осуществляется через JSON‑файлы (`fsm_state.json`, `telemetry.json`, `sensors.json`, `shared_bus.json`). Проект работает в терминальных средах, включая Termux.

### Быстрый запуск
1. Установите зависимости: `pip install -r requirements.txt`.
2. Запустите все процессы: `bash run_all.sh`.

### Тесты
Для запуска тестов выполните `pytest -q`.


## File overview

### Root scripts
- `assistant.py` - CLI interface for sending commands and interacting with agents
- `event_trigger.py` - simple helper to post events to the FSM
- `navigation_monitor.py` - logs navigation related telemetry
- `operator_interface.py` - text interface with commands like `status` and `agents`
- `power_core.py` - simulates basic power management cycle
- `sensor_manager_demo.py` - demo runner for the sensor subsystem
- `sensor_overlay.py` - tiny terminal overlay with live sensor data
- `state_monitor.py` - prints FSM state changes to console
- `status_hud.py` - curses-based heads-up display for key metrics
- `system_diagnostics.py` - quick diagnostics of JSON files and health
- `voice_logger.py` - records spoken messages to `logs/` with timestamps

### JSON data
- `fsm_state.json` - finite state machine state
- `telemetry.json` - latest telemetry data
- `mission_state.json` - mission progress tracker
- `mission_status.json` - active mission status
- `shared_bus.json` - inter-agent communication hub
- `task_state.json` - tasks assigned to agents
- `sensors.json` - aggregated sensor readings
- `qiki_boot_log.json` - boot timestamp log

### Shell scripts
- `run_all.sh` - launches all background modules
- `start.sh` - helper for Termux installation

### Config files
- `config/bot_specs.json` - hardware capabilities
- `config/locales.json` - localization strings
- `config/mission.json` - predefined missions
- `config/rules.json` - rule engine definitions

### Core modules (`core/`)
- `agent_comm.py` - basic agent messaging API
- `agent_comm_link.py` - simulates a comm link between agents
- `agent_ping.py` - heartbeat updater for agents
- `agent_profile.py` - metadata for each agent
- `auto_controller.py` - automatic event generator
- `file_paths.py` - constants for all data file paths
- `fsm_client.py` - safe read/write access to FSM JSON
- `fsm_core.py` - in-memory finite state machine
- `fsm_gatekeeper.py` - centralized FSM logging
- `fsm_interface.py` - high level FSM API
- `fsm_io.py` - queue and lock management for FSM
- `fsm_logger.py` - writes detailed FSM logs
- `localization_manager.py` - bilingual text helper
- `mission_executor.py` - executes missions from config
- `rule_engine.py` - evaluates triggers and rules
- `sensor_preprocessor.py` - filters raw sensor data
- `shared_bus_manager.py` - maintains shared_bus.json
- `shared_json_cache.py` - RAM cache for frequently read JSON
- `system_health_monitor.py` - checks agent heartbeats and file freshness
- `telemetry.py` - telemetry recorder and access layer

### CLI interface (`interfaces/cli/`)
- `agent_control_panel.py` - interactive control interface
- `agent_monitor.py` - watch list of agents from shared bus
- `cli_dashboard.py` - curses dashboard of FSM and telemetry
- `system_dashboard.py` - summary view of system health

### Sensors subsystem (`sensors/`)
- `sensor_bus.py` - orchestrates sensor cluster updates
- `clusters/base_cluster.py` - common base for clusters
- `clusters/communication.py` - communications status sensors
- `clusters/environment.py` - environment readings
- `clusters/ew.py` - electronic warfare metrics
- `clusters/navigation.py` - attitude and position sensors
- `clusters/power.py` - power supply monitors
- `clusters/proximity.py` - proximity and collision detection
- `clusters/rlsm.py` - radar/lidar sensor model
- `clusters/structural.py` - structural integrity sensors
- `clusters/system_health.py` - system temperature and faults
- `clusters/thermal.py` - thermal management sensors
- `clusters/thrusters.py` - thruster status readings

### Machine learning (`ml/`)
- `ml_predict.py` - tiny example prediction helper
- `micrograd/` - bundled copy of the Micrograd library

### Simulation
- `simulation/physics_engine.py` - simple physics simulation for demos

### Prompts
- files in `prompts/` contain design notes and development plans

### Tools
- `agent_initializer.py` - sets up initial JSON files
- `consistency_checker.py` - validates cross-module data
- `fsm_debugger.py` - helper to inspect FSM state
- `json_cache_debugger.py` - view contents of shared_json_cache
- `monitor.py` - script to follow log files
- `rule_engine_demo.py` - showcase of the rule engine
- `system_health_monitor.py` - CLI monitor of agent heartbeats
- `system_monitor.py` - continuous system metrics display
- `watchdog_monitor.py` - restarts modules if they hang

### Tests
- `tests/test_fsm_core.py` - unit tests for the FSM logic
- `tests/test_fsm.py` - integration tests of core FSM operations
- `tests/test_sensor_preprocessor.py` - checks sensor preprocessing
- `tests/test_telemetry_cycle.py` - verifies telemetry read/write loop
- `tests/cli_scenario_tester.py` - scenario runner for CLI modules
- `tests/scenarios/simple_movement.json` - sample mission scenario


## Обзор файлов

Те же сведения представлены ниже по‑русски.

### Скрипты в корне
- `assistant.py` – интерфейс командной строки для отправки команд агентам
- `event_trigger.py` – утилита для публикации событий в FSM
- `navigation_monitor.py` – логирование навигационных данных
- `operator_interface.py` – текстовый интерфейс с командами `status` и `agents`
- `power_core.py` – простая логика управления питанием
- `sensor_manager_demo.py` – демонстрация сенсорной подсистемы
- `sensor_overlay.py` – маленькое наложение сенсоров в терминале
- `state_monitor.py` – вывод изменений состояния FSM
- `status_hud.py` – curses‑HUD с ключевой информацией
- `system_diagnostics.py` – быстрая проверка JSON‑файлов
- `voice_logger.py` – записывает голосовые сообщения в папку `logs/`

### JSON‑данные
- `fsm_state.json` – текущее состояние FSM
- `telemetry.json` – последняя телеметрия
- `mission_state.json` – прогресс выполнения миссий
- `mission_status.json` – статус текущей миссии
- `shared_bus.json` – шина обмена агентами
- `task_state.json` – задачи для агентов
- `sensors.json` – агрегированные показания сенсоров
- `qiki_boot_log.json` – журнал запусков

### Скрипты оболочки
- `run_all.sh` – запускает все фоновые модули
- `start.sh` – помощник для Termux

### Конфигурация
- `config/bot_specs.json` – характеристики оборудования
- `config/locales.json` – строки локализации
- `config/mission.json` – предопределенные миссии
- `config/rules.json` – правила для движка

### Модули ядра (`core/`)
- `agent_comm.py` – API обмена сообщениями между агентами
- `agent_comm_link.py` – симулятор канала связи
- `agent_ping.py` – обновление heartbeat агентов
- `agent_profile.py` – метаданные агента
- `auto_controller.py` – генератор автоматических событий
- `file_paths.py` – константы путей к файлам
- `fsm_client.py` – безопасный доступ к FSM-файлам
- `fsm_core.py` – реализация конечного автомата
- `fsm_gatekeeper.py` – централизованный логгер FSM
- `fsm_interface.py` – высокоуровневый API FSM
- `fsm_io.py` – очереди и блокировки FSM
- `fsm_logger.py` – детальное логирование FSM
- `localization_manager.py` – двуязычные сообщения
- `mission_executor.py` – выполнение миссий
- `rule_engine.py` – обработка правил и триггеров
- `sensor_preprocessor.py` – фильтрация сырых сенсорных данных
- `shared_bus_manager.py` – управление файлом shared_bus
- `shared_json_cache.py` – кэш JSON‑файлов в памяти
- `system_health_monitor.py` – контроль heartbeat и свежести файлов
- `telemetry.py` – запись и доступ к телеметрии

### CLI-интерфейсы (`interfaces/cli/`)
- `agent_control_panel.py` – интерактивное управление
- `agent_monitor.py` – список агентов из шины
- `cli_dashboard.py` – curses-панель FSM и телеметрии
- `system_dashboard.py` – сводная панель состояния

### Сенсоры (`sensors/`)
- `sensor_bus.py` – координирует обновление кластеров
- `clusters/base_cluster.py` – базовый класс кластера
- `clusters/communication.py` – сенсоры связи
- `clusters/environment.py` – сенсоры окружающей среды
- `clusters/ew.py` – электронная борьба
- `clusters/navigation.py` – сенсоры ориентации и положения
- `clusters/power.py` – мониторинг питания
- `clusters/proximity.py` – обнаружение препятствий
- `clusters/rlsm.py` – модель радара/лидара
- `clusters/structural.py` – целостность конструкции
- `clusters/system_health.py` – температура и сбои
- `clusters/thermal.py` – управление температурой
- `clusters/thrusters.py` – состояние движителей

### Машинное обучение (`ml/`)
- `ml_predict.py` – пример предсказаний
- `micrograd/` – встроенная библиотека Micrograd

### Симуляция
- `simulation/physics_engine.py` – простая физическая модель

### Подсказки
- файлы в `prompts/` содержат заметки и планы разработки

### Инструменты
- `agent_initializer.py` – создает начальные JSON
- `consistency_checker.py` – проверяет согласованность данных
- `fsm_debugger.py` – инспекция FSM
- `json_cache_debugger.py` – просмотр кэша JSON
- `monitor.py` – следит за логами
- `rule_engine_demo.py` – демонстрация движка правил
- `system_health_monitor.py` – монитор heartbeat через CLI
- `system_monitor.py` – непрерывный вывод метрик
- `watchdog_monitor.py` – перезапуск модулей при зависании

### Тесты
- `tests/test_fsm_core.py` – модульные тесты FSM
- `tests/test_fsm.py` – интеграционные тесты FSM
- `tests/test_sensor_preprocessor.py` – тесты предобработки сенсоров
- `tests/test_telemetry_cycle.py` – цикл записи/чтения телеметрии
- `tests/cli_scenario_tester.py` – прогон сценариев CLI
- `tests/scenarios/simple_movement.json` – пример сценария миссии

