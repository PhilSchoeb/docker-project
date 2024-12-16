import streamlit as st
import pandas as pd
import requests
import json
import wandb
import plotly.express as px
from ift6758.client.serving_client import ServingClient
from ift6758.client.game_client import GameClient

# Initialize serving and game clients
game_client = GameClient(ip="127.0.0.1", port=8000)
serving_client = ServingClient(ip="127.0.0.1", port=8000)

# config streamlit
st.set_page_config(
    page_title="Hockey Visualization App",
    layout="wide"
)
st.title("Hockey Visualization App")

# init de WandB
st.sidebar.header("WandB Configuration")
workspace = st.sidebar.text_input("Workspace", placeholder="Enter WandB workspace name")
model = st.sidebar.text_input("Model", placeholder="Enter model name")
version = st.sidebar.text_input("Version", placeholder="Enter model version")

# Button to load model
if st.sidebar.button("Get model"):
    try:
        response = serving_client.download_registry_model(workspace, model, version)
        st.sidebar.write(response.json())
    except Exception as e:
        st.sidebar.error(f"An error occurred: {e}")

# ID du match
game_id = st.text_input("Game ID", placeholder="Enter Game ID (e.g., 2021020329)")

if model == "goal_angle_regression":
    required_features = ["goal_angle"]
elif model == "goal_distance_regression":
    required_features = ["goal_distance"]
elif model == "goal_distance_and_angle_regression":
    required_features = ["goal_distance","goal_angle"]

# Button to ping game and fetch live game data
if st.button("Ping game"):
    try:

        # Fetch live game events and process them dynamically
        for events_df, is_live in game_client.download_live_game_events(interval=10, game_id = game_id):

            # Filter only the columns required for prediction
            prediction_data = events_df[required_features]

            # Make predictions on currently loaded events using the ServingClient
            predictions = serving_client.predict(prediction_data)
        
            st.subheader("Data used for predictions (and predictions)")
            st.dataframe(predictions)

    except Exception as e:
        st.error(f"An error occurred: {e}")
