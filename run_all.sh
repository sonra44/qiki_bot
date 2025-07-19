#!/bin/bash

echo "[QIKI] Starting system with FSM Lockdown Architecture..."

# Set PYTHONPATH to allow imports from the project root
export PYTHONPATH=/data/data/com.termux/files/home/qiki_bot:$PYTHONPATH

# --- STAGE 1: SYNCHRONOUS INITIALIZATION ---
# This script runs to completion before anything else starts.
# It ensures all data files are created and ready.
echo "[QIKI] Running data and agent initializer..."
python3 /data/data/com.termux/files/home/qiki_bot/tools/agent_initializer.py

# --- STAGE 2: LAUNCH FSM GATEKEEPER ---
# This is the most critical process and must be started first.
echo "[QIKI] Launching FSM Gatekeeper..."
python3 /data/data/com.termux/files/home/qiki_bot/core/fsm_gatekeeper.py &

# --- STAGE 3: SHORT PAUSE ---
# Give the Gatekeeper a moment to start up and acquire locks.
echo "[QIKI] Pausing for 1 second to allow Gatekeeper to initialize..."
sleep 1

# --- STAGE 4: LAUNCH ALL OTHER BACKGROUND COMPONENTS ---
echo "[QIKI] Launching all other background components..."
python3 /data/data/com.termux/files/home/qiki_bot/simulation/physics_engine.py &
echo "[QIKI] Launched physics_engine.py"
python3 /data/data/com.termux/files/home/qiki_bot/sensors/sensor_bus.py &
echo "[QIKI] Launched sensor_bus.py"
python3 /data/data/com.termux/files/home/qiki_bot/core/auto_controller.py &
echo "[QIKI] Launched auto_controller.py"
python3 /data/data/com.termux/files/home/qiki_bot/core/agent_comm_link.py &
echo "[QIKI] Launched agent_comm_link.py"
python3 /data/data/com.termux/files/home/qiki_bot/tools/system_health_monitor.py &
echo "[QIKI] Launched system_health_monitor.py"
python3 /data/data/com.termux/files/home/qiki_bot/tools/system_monitor.py &
echo "[QIKI] Launched system_monitor.py"

# --- STAGE 5: LAUNCH STRATEGIC EXECUTOR ---
echo "[QIKI] Launching Mission Executor..."
python3 /data/data/com.termux/files/home/qiki_bot/core/mission_executor.py &
echo "[QIKI] Launched mission_executor.py"

echo "[QIKI] All background components launched."
echo "[QIKI] To monitor FSM logs: tail -f /data/data/com.termux/files/home/qiki_bot/logs/fsm_log.txt"
echo "[QIKI] To launch CLI dashboard: python3 /data/data/com.termux/files/home/qiki_bot/interfaces/cli/cli_dashboard.py"
