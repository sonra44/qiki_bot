#/data/data/com.termux/files/usr/bin/bash

# Set PYTHONPATH to include the project root
export PYTHONPATH=/data/data/com.termux/files/home/qiki_bot:$PYTHONPATH

echo "[QIKI BOT] Development script. Use 'run_all.sh' for full system start."

if [ "$1" = "sim" ]; then
  echo "[QIKI BOT] Starting Physics Engine..."
  python3 /data/data/com.termux/files/home/qiki_bot/simulation/physics_engine.py
elif [ "$1" = "auto" ]; then
  echo "[QIKI BOT] Starting Auto Controller..."
  python3 /data/data/com.termux/files/home/qiki_bot/core/auto_controller.py
elif [ "$1" = "cli" ]; then
  echo "[QIKI BOT] Starting CLI Dashboard..."
  python3 /data/data/com.termux/files/home/qiki_bot/interfaces/cli/cli_dashboard.py
elif [ "$1" = "sensors" ]; then
  echo "[QIKI BOT] Starting Sensor Bus..."
  python3 /data/data/com.termux/files/home/qiki_bot/sensors/sensor_bus.py
elif [ "$1" = "assistant" ]; then
  echo "[QIKI BOT] Starting Assistant..."
  python3 /data/data/com.termux/files/home/qiki_bot/assistant.py
else
  echo "Usage: $0 {sim|auto|cli|sensors|assistant}"
fi
