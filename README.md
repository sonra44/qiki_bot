# QIKI Bot

QIKI Bot is a minimal multi-agent system built with pure Python and JSON. Communication between modules occurs only through local JSON files, making it easy to run even in restricted or offline environments.

## Project layout
- `core/` — state machine and shared bus utilities
- `sensors/` — sensor clusters and simulator
- `interfaces/cli/` — command-line dashboards
- `tools/` — helper scripts
- `simulation/` — simple physics engine

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

## Русская версия

**QIKI Bot — минимальная система из нескольких агентов, построенная на чистом Python и JSON.** Все модули обмениваются данными через локальные JSON-файлы, что упрощает запуск проекта даже в ограниченных или офлайн средах.

### Структура проекта
- `core/` — машина состояний и общая шина
- `sensors/` — кластеры сенсоров и симулятор
- `interfaces/cli/` — панели командной строки
- `tools/` — вспомогательные скрипты
- `simulation/` — простой физический движок

### Быстрый старт
1. Установите зависимости:
   ```bash
   pip install -r requirements.txt
```bash
pytest -q
```
