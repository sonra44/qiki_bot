import os
import sys

# Add project root to be able to import core modules
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

from core.rule_engine import RuleEngine

print("--- Testing RuleEngine in isolation ---")

# Initialize the engine
re = RuleEngine()

# The engine loads rules on init, let's check them
print(f"[RULES LOADED] ({len(re.rules)} rules)")
for rule in re.rules:
    print(f"  - Priority {rule.get('priority')}: {rule.get('name')}")

# Manually create some data to force a rule to trigger
# Let's force the 'LowBatteryCharge' rule
re.telemetry_manager.update({"battery_percent": 15.0})
re.fsm.state = "idle" # Manually set in-memory state for this test

print("\n--- Evaluating rules with low battery... ---")

# run_once() should now return the event name
proposed_event = re.run_once()

print(f"\n[EVENT PROPOSED] '{proposed_event}'")

if proposed_event == "charge":
    print("\n[SUCCESS] RuleEngine correctly proposed the 'charge' event.")
else:
    print(f"\n[FAILURE] RuleEngine proposed '{proposed_event}' instead of 'charge'.")

print("--- Test Complete ---")
