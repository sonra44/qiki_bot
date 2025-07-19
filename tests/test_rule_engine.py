import os
import sys
import json

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(PROJECT_ROOT)

from core.rule_engine import RuleEngine


def test_rule_cache_reload(tmp_path):
    rules_path = tmp_path / "rules.json"
    with open(rules_path, "w") as f:
        json.dump([
            {"name": "Low", "condition": "telemetry.battery_percent < 50", "action": "charge", "priority": 1}
        ], f)

    engine = RuleEngine(rule_path=str(rules_path))
    assert len(engine.rules) == 1

    # modify file but cached rules should remain until reload
    with open(rules_path, "w") as f:
        json.dump([], f)
    assert len(engine.rules) == 1

    engine.reload_rules()
    assert len(engine.rules) == 0


def test_rule_evaluate(tmp_path):
    rules_path = tmp_path / "rules.json"
    rule = {"name": "Low", "condition": "telemetry.battery_percent < 50", "action": "charge", "priority": 1}
    with open(rules_path, "w") as f:
        json.dump([rule], f)

    engine = RuleEngine(rule_path=str(rules_path))
    triggered = engine.evaluate({"battery_percent": 40}, "idle")
    assert triggered and triggered[0]["action"] == "charge"

