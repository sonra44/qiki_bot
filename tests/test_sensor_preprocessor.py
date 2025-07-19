import os
import sys

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(PROJECT_ROOT)

from core.sensor_preprocessor import SensorPreprocessor


def test_collect_statuses():
    raw = {
        "cluster1": {"status": "OK", "errors": []},
        "cluster2": {"status": "ERROR", "errors": ["x"]},
    }
    proc = SensorPreprocessor(raw)
    statuses = proc.collect_statuses()
    assert statuses == {"cluster1": "OK", "cluster2": "ERROR"}
