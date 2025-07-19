import sys
import os
import json

# Add the project root to the sys.path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(project_root)

def test_telemetry_file():
    telemetry_path = os.path.join(project_root, "telemetry.json")
    assert os.path.exists(telemetry_path), "telemetry.json does not exist"
    with open(telemetry_path) as f:
        data = json.load(f)
        assert "battery_percent" in data
