import pandas as pd
from ift6758.client.serving_client import ServingClient
from ift6758.client.game_client import GameClient

#Test serving_client
# Initialize client
client = ServingClient(ip="127.0.0.1", port=8000)

# Test /predict endpoint
df = pd.read_csv("serving/test_data_2022.csv")
data = df[["goal_distance"]].head(5)
print("Sending data for prediction...")
predictions = client.predict(data)
print("Predictions:")
print(predictions)

# Test /logs endpoint
print("Retrieving server logs...")
logs = client.logs()
print("Logs:")
for log in logs:
    print(log)

# Test /download_registry_model endpoint
print("Downloading a new model...")
result = client.download_registry_model(workspace="simple_model_logistic_regression", model="goal_angle_regression", version="v0")
print("Download result:")
print(result)



