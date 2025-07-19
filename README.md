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

