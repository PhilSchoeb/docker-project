'''
This file contains examples on how app.py can be used and it can also serve as a test for the application.
'''
import requests
import json
import pandas as pd

BASE_URL = "http://127.0.0.1:8000"


# Test get /logs
response = requests.get(BASE_URL + "/logs")

print("get /logs test")
print(f'Status Code: {response.status_code}')
print(f'Response JSON: {response.json()}')
print("\n")


# Test post /download_registry_model

# Fake model
message = '[{"project": "simple_model_logistic_regression", "model": "imaginary", "version": "v4"}]'
response = requests.post(BASE_URL + "/download_registry_model", json=json.loads(message))

print("post /download_registry_model test with fake model")
print(f'Status Code: {response.status_code}')
print(f'Response JSON: {response.json()}')

# Existing model
message = '[{"project": "simple_model_logistic_regression", "model": "goal_distance_and_angle_regression", "version": "v0"}]'
response = requests.post(BASE_URL + "/download_registry_model", json=json.loads(message))

print("post /download_registry_model test with existing model")
print(f'Status Code: {response.status_code}')
print(f'Response JSON: {response.json()}')


# Test post /predict

# With goal_distance_and_angle_regression model
df = pd.read_csv("./test_data_2022.csv")
# If you want to test other models, make sure to keep the right features according to the model
X = df[["goal_distance", "goal_angle"]].head(5)
message = X.to_json()
response = requests.post(BASE_URL + "/predict", json=json.loads(message))

print("post /predict test")
print(f'Status Code: {response.status_code}')
print(f'Response JSON: {response.json()}')


# Last test, switch to goal_distance_regression model and predict with it
message = '[{"project": "simple_model_logistic_regression", "model": "goal_distance_regression", "version": "v0"}]'
response = requests.post(BASE_URL + "/download_registry_model", json=json.loads(message))

df = pd.read_csv("./test_data_2022.csv")
X = df[["goal_distance"]].head(5)
message = X.to_json()
response = requests.post(BASE_URL + "/predict", json=json.loads(message))