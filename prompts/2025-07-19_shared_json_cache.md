
Создай модуль: qiki_bot/core/shared_json_cache.py

Цель: Централизованный доступ к frequently-used JSON-файлам (telemetry.json, fsm_state.json, mission_status.json) через RAM-кэш, с автообновлением в фоне.

1. Архитектура:
   - Используй `threading.Thread` или `asyncio` для фонового наблюдения за файлами.
   - Поддерживай кэш в виде dict внутри Python (в RAM).
   - Используй `file_mod_time` или `watchdog` для отслеживания изменений (по ситуации).
   - Поддержи перезапись файла: запись в файл только если данные изменились.

2. Интерфейс:
   - get_json(path: str) → возвращает dict (из RAM)
   - set_json(path: str, data: dict) → обновляет кэш, записывает в файл только при изменении
   - refresh(path) → принудительная перезагрузка из файла
   - start_cache_watcher() → запускает мониторинг изменений

3. Минимально поддерживаемые пути:
   - telemetry.json
   - fsm_state.json
   - mission_status.json

4. Интеграция:
   - Обнови fsm_io, sensor_preprocessor, и CLI-интерфейс для использования shared_json_cache вместо `open(...)`
   - Сделай это **опционально** (можно оставить fallback на прямой доступ в legacy-режиме)

5. CLI-доступ:
   - Создай файл `tools/json_cache_debugger.py`
     - Команды: `list`, `get <path>`, `refresh <path>`, `flush`
     - Поможет при отладке и горячей замене данных
