
Создай модуль qiki_bot/tools/consistency_checker.py.

Цель: Проверка целостности данных между FSM, telemetry.json, и mission_status.json.

1. Основная логика:
   - Каждые N секунд (по умолчанию: 1 секунда) проверять согласованность между:
     - fsm_io.get_current_state()
     - содержимым telemetry.json
     - содержимым mission_status.json

2. Реализуй проверки:
   - Если FSM в состоянии "CHARGING", но battery_level >= 95% → warning.
   - Если FSM в "CRITICAL", но все сенсоры "OK" → flag anomaly.
   - Если в telemetry отсутствуют обязательные ключи (навигация, питание, термоконтроль) → log error.
   - Если миссия помечена как "COMPLETE", но FSM всё ещё в "MISSION_ACTIVE" → несогласованность.

3. Логгирование:
   - Все найденные несоответствия логировать в system_integrity.log.
   - Визуализатор может читать последнюю строку лога для отображения состояния ("OK", "ANOMALY", "ERROR").

4. CLI-интерфейс:
   - Поддержи вызов через CLI: `python3 consistency_checker.py --once` и `--watch`
   - --once — однократная проверка
   - --watch — запуск в цикле с интервалом

5. Обнови документацию:
   - Добавь информацию в README.md и PROMT.md о том, как используется consistency_checker.
