##  **ЭТАП 4э: TTL / Heartbeat для агентов (`agent_comm.py`)**

###  Цель:

Добавить механизм «живости» (heartbeat) для всех активных агентов, чтобы система могла определять:

* какие агенты активны
* кто «завис» (перестал пинговаться)
* кто ещё ни разу не был замечен (unknown)

---

##  **Что конкретно нужно сделать:**

### 1. В `agent_comm.py`:

* Добавить новое поле: `last_heartbeat` (в формате UTC ISO 8601).
* Агенты при каждой активности (или каждые ~1–2 сек) **обновляют это поле в `shared_bus.json`**.

### 2. В `system_health_monitor.py`:

* Проверять, **когда последний раз был обновлён `last_heartbeat`**.
* Если прошло больше 3 сек → агент считается `STALE`.
* Если больше 10 сек → `DEAD`.

### 3. В `logs/agent_health.log`:

* Писать статус по каждому агенту:

  ```
  [2025-07-18 17:41:08] Agent 'alpha-01' → OK
  [2025-07-18 17:41:08] Agent 'beta-03' → STALE (last seen: 17:40:58)
  ```

---

##  Дополнительно:

* Использовать `time.time()` или `datetime.utcnow().isoformat()`.
* Не нарушать структуру `shared_bus.json`.
* Новый ключ:

  ```json
  "agents": {
    "alpha-01": {
      "status": "ACTIVE",
      "last_heartbeat": "2025-07-18T17:41:08Z"
    }
  }
  ```

---

##  **ПРОМТ для Gemini CLI:**

```
Приступай к этапу 4э: TTL / Heartbeat агентов.

1. Добавь в `agent_comm.py` механизм `last_heartbeat`, который обновляет метку времени при активности агента в `shared_bus.json`.
2. Создай в `system_health_monitor.py` проверку всех агентов: если heartbeat > 3 сек → STALE, если > 10 сек → DEAD.
3. Записывай статус в `logs/agent_health.log` в удобочитаемом формате.
4. Не нарушай текущую структуру `shared_bus.json`, добавляй поля аккуратно.
5. После завершения — сообщи, что можно тестировать.
```

---

✅ Как только Gemini CLI выполнит задачу — дай знать, и мы переходим к **валидации и следующему этапу 5**.