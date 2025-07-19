import sys
import os
import random
import json

# Add micrograd to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'micrograd')))

from micrograd.engine import Value
from micrograd.nn import MLP

class BatteryPredictor:
    def __init__(self):
        # Define the neural network: 3 inputs, 1 hidden layer with 4 neurons, 1 output
        self.model = MLP(3, [4, 1])
        self.trained = False

    def generate_synthetic_data(self, num_samples=100):
        data = []
        for _ in range(num_samples):
            power_wh = random.uniform(100, 500) # Current battery charge
            consumption_w = random.uniform(10, 120) # Current power consumption
            speed_mps = random.uniform(0, 1.2) # Current speed

            # Simulate battery change over 10 seconds
            # Assuming consumption is constant over 10 seconds
            # Energy change = (consumption_w / 3600) * 10 seconds
            energy_change_wh = (consumption_w / 3600.0) * 10
            
            # Target: battery charge after 10 seconds
            target_power_wh = max(0, power_wh - energy_change_wh)
            
            data.append({
                "power_wh": power_wh,
                "consumption_w": consumption_w,
                "speed_mps": speed_mps,
                "target": target_power_wh
            })
        return data

    def train_model(self, data, epochs=100, learning_rate=0.01):
        xs = [[d["power_wh"], d["consumption_w"], d["speed_mps"]] for d in data]
        ys = [[d["target"]] for d in data]

        for k in range(epochs):
            # forward pass
            ypred = [self.model(list(map(Value, x))) for x in xs]
            loss = sum((yout[0] - Value(ygt[0]))**2 for yout, ygt in zip(ypred, ys))

            # backward pass
            for p in self.model.parameters():
                p.grad = 0.0
            loss.backward()

            # update
            for p in self.model.parameters():
                p.data -= learning_rate * p.grad

            if k % 10 == 0:
                print(f"Epoch {k}, Loss: {loss.data}")
        self.trained = True

    def predict_future_battery(self, telemetry_dict):
        if not self.trained:
            print("Warning: Model not trained. Training with synthetic data...")
            synthetic_data = self.generate_synthetic_data()
            self.train_model(synthetic_data)

        power_wh = telemetry_dict.get("power_wh", 0.0)
        consumption_w = telemetry_dict.get("consumption_w", 0.0)
        speed_mps = telemetry_dict.get("speed_mps", 0.0)

        # Create Value objects for input
        input_values = [Value(power_wh), Value(consumption_w), Value(speed_mps)]
        
        # Make prediction
        predicted_output = self.model(input_values)
        return predicted_output[0].data # Assuming single output

if __name__ == "__main__":
    predictor = BatteryPredictor()
    
    # Generate and train with synthetic data
    print("Generating synthetic data...")
    synthetic_data = predictor.generate_synthetic_data(num_samples=500)
    print("Training model...")
    predictor.train_model(synthetic_data, epochs=200, learning_rate=0.001)

    # Example prediction using dummy telemetry data
    print("\nMaking example prediction...")
    dummy_telemetry = {
        "power_wh": 400.0,
        "consumption_w": 50.0,
        "speed_mps": 0.5
    }
    predicted_wh = predictor.predict_future_battery(dummy_telemetry)
    print(f"Current: {dummy_telemetry['power_wh']} Wh, Consumption: {dummy_telemetry['consumption_w']} W, Speed: {dummy_telemetry['speed_mps']} m/s")
    print(f"Predicted battery (10s future): {predicted_wh:.2f} Wh")

    dummy_telemetry_low_charge = {
        "power_wh": 50.0,
        "consumption_w": 100.0,
        "speed_mps": 1.0
    }
    predicted_wh_low = predictor.predict_future_battery(dummy_telemetry_low_charge)
    print(f"\nCurrent: {dummy_telemetry_low_charge['power_wh']} Wh, Consumption: {dummy_telemetry_low_charge['consumption_w']} W, Speed: {dummy_telemetry_low_charge['speed_mps']} m/s")
    print(f"Predicted battery (10s future): {predicted_wh_low:.2f} Wh")
