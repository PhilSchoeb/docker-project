import streamlit as st
import pandas as pd
import requests
import json
import wandb
import time
import threading
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
workspace = st.sidebar.text_input("Workspace", value = "simple_model_logistic_regression", placeholder="Enter WandB workspace name")
model = st.sidebar.text_input("Model", value = "goal_distance_regression", placeholder="Enter model name")
version = st.sidebar.text_input("Version", value = "v0", placeholder="Enter model version")

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

        game_data = game_client.download_live_game_information(game_id = game_id)

        home_team = game_data['home_team']
        away_team = game_data['away_team']

        st.subheader(f"Game {game_id}: {home_team} vs {away_team}")

        # Placeholder for the timer
        timer_placeholder = st.empty()
        
        # Create placeholders for the xG metrics
        col1, col2 = st.columns(2)
        xg_home_placeholder = col1.empty()
        xg_away_placeholder = col2.empty()

        st.subheader("Data used for predictions and associated predictions")

        # Placeholder for the events dataframe 
        events_placeholder = st.empty()

        # Initialize an empty dataframe to collect all data
        all_data = pd.DataFrame() 

        # Fetch live game events and process them dynamically
        for events_data in game_client.download_live_game_events(game_id = game_id, features = required_features):

            events_df = events_data['new_events']

            # Access the time and period data
            time_left = events_data['live_data']['time']
            period = events_data['live_data']['period']
            home_score = events_data['live_data']['home_score']
            away_score = events_data['live_data']['away_score']
            xG_home = events_data['live_data']['xG_home']
            xG_away = events_data['live_data']['xG_away']

            if events_df is not None:
                # Display columns of interest
                # prediction_data = events_df[required_features]

                # Update displayed dataframe
                all_data = pd.concat([all_data, events_df], ignore_index=True)


            # Update the dataframe dynamically
            with events_placeholder.container():
                st.dataframe(all_data)

            # Update the scores and xG dynamically 
            with xg_home_placeholder.container():
                xg_home_placeholder.metric(
                    label=f"{home_team} xG (actual)",
                    value=f"{xG_home} ({home_score})",
                    delta=round(xG_home - home_score, 2)  
                )
                
            with xg_away_placeholder.container():
                xg_away_placeholder.metric(
                    label=f"{away_team} xG (actual)",
                    value=f"{xG_away} ({away_score})",
                    delta=round(xG_away - away_score, 2) 
                )

            # Update timer and period dynamically
            with timer_placeholder.container():
                minutes, seconds = divmod(time_left, 60)
                formatted_time = f"{minutes:02d}:{seconds:02d}"
                st.write(f"Period: {period} - {formatted_time}  left: ")

            time.sleep(1)


    except Exception as e:
        st.error(f"An error occurred: {e}")
