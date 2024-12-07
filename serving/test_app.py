import requests
import json

BASE_URL = "http://0.0.0.0:8000"

# Test get /logs
response = requests.get(BASE_URL + "/logs")

print("get /logs test")
print(f'Status Code: {response.status_code}')
print(f'Response JSON: {response.json()}')
print("\n")

# Test post /download_registry_model
# Existing model
message = '[{"project": "simple_model_logistic_regression", "model": "goal_angle_regression", "version": "v0"}]'
response = requests.post(BASE_URL + "/download_registry_model", json=json.loads(message))

print("post /download_registry_model test with existing model")
print(f'Status Code: {response.status_code}')
print(f'Response JSON: {response.json()}')

# Fake model
message = '[{"project": "simple_model_logistic_regression", "model": "imaginary", "version": "v4"}]'
response = requests.post(BASE_URL + "/download_registry_model", json=json.loads(message))

print("post /download_registry_model test with fake model")
print(f'Status Code: {response.status_code}')
print(f'Response JSON: {response.json()}')

# Existing model
message = '[{"project": "simple_model_logistic_regression", "model": "goal_distance_and_angle_regression", "version": "v0"}]'
response = requests.post(BASE_URL + "/download_registry_model", json=json.loads(message))

print("post /download_registry_model test with fake model")
print(f'Status Code: {response.status_code}')
print(f'Response JSON: {response.json()}')

# Test post /predict
