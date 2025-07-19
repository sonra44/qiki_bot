## ✅ PROMPT 6: `watchdog_monitor.py` — Страж живости файлов и процессов

````
Цель: Следить за ключевыми файлами и подсистемами. Если какой-либо файл не обновлялся слишком долго — сигнализировать об этом как о сбое.

Создай файл: `tools/watchdog_monitor.py`

1. Мониторинг файлов:
   - `telemetry.json`
   - `fsm_state.json`
   - `task_state.json`
   - `mission_file.json`
   - (опционально) любые `.log` или `vision_output.json`

2. Логика:
   - Проверяет timestamp последнего изменения файлов (через `os.path.getmtime`)
   - Если файл не обновлялся более **3 секунд** → флаг `STALE`
   - Если файл не существует → флаг `MISSING`
   - Если файл резко изменён (размер или пустота) → `CORRUPTED`

3. Вывод:
   - В лог: `logs/watchdog_status.json`
     ```json
     {
       "timestamp": "2025-07-18T18:43:00Z",
       "telemetry.json": "STALE",
       "fsm_state.json": "OK",
       "task_state.json": "OK",
       "mission_file.json": "MISSING"
     }
     ```
   - При запуске в терминале (`--verbose`) — вывод в стиле QIKI:
     ```
     [WDG] fsm_state.json : OK
     [WDG] telemetry.json : STALE (Last update: 3.7s ago)
     [WDG] mission_file.json : MISSING
     ```

4. CLI-флаги:
   - `--watch` — постоянный режим (раз в 1 сек)
   - `--once` — однократный проход
   - `--log` — включить запись в лог
   - `--exit-on-fail` — завершать скрипт при критическом статусе

5. Расширения:
   - Позже можно интегрировать в HUD-интерфейс или терминал cockpit
   - Можно отправлять сообщения в FSM, если файл слишком долго в `STALE`

````