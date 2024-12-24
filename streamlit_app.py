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
import os

GAME_CLIENT_HOST = os.environ.get("GAME_CLIENT_HOST", "127.0.0.1")
GAME_CLIENT_PORT = os.environ.get("GAME_CLIENT_PORT", "8000")
SERVING_CLIENT_HOST = os.environ.get("SERVING_CLIENT_HOST", "127.0.0.1")
SERVING_CLIENT_PORT = os.environ.get("SERVING_CLIENT_PORT", "8000")

# Initialize serving and game clients
game_client = GameClient(ip=GAME_CLIENT_HOST, port=GAME_CLIENT_PORT)
serving_client = ServingClient(ip=SERVING_CLIENT_HOST, port=SERVING_CLIENT_PORT)

# config streamlit
st.set_page_config(
    page_title="Hockey Visualization App",
    layout="wide"
)
st.title("Hockey Visualization App")

# init de WandB
st.sidebar.header("WandB Configuration")
workspace = st.sidebar.text_input("Workspace", value="simple_model_logistic_regression", placeholder="Enter WandB workspace name")
model = st.sidebar.text_input("Model", value="goal_distance_regression", placeholder="Enter model name")
version = st.sidebar.text_input("Version", value="v0", placeholder="Enter model version")

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
        game_data = game_client.download_live_game_information(game_id=game_id)

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

        # Initialize an empty dataframe to collect all data
        all_data = pd.DataFrame() 

        # Placeholder for the events dataframe 
        events_placeholder = st.empty()

        # Placeholder for the top players table
        top_players_placeholder = st.empty()

        # Fetch live game events and process them dynamically
        for events_data in game_client.download_live_game_events(game_id=game_id, features=required_features):

            events_df = events_data['new_events']

            # Access the time and period data
            time_left = events_data['live_data']['time']
            period = events_data['live_data']['period']
            home_score = events_data['live_data']['home_score']
            away_score = events_data['live_data']['away_score']
            xG_home = events_data['live_data']['xG_home']
            xG_away = events_data['live_data']['xG_away']

            if events_df is not None:
                # Update displayed dataframe
                all_data = pd.concat([all_data, events_df], ignore_index=True)

                # Bonus feature: Update top players by xG dynamically
                if 'shooting_player_name' in all_data.columns and 'goal_prob' in all_data.columns and 'shooting_player_team_id' in all_data.columns:
                    top_xg_players = (
                        all_data.groupby(['shooting_player_name', 'shooting_player_team_id'])['goal_prob']
                        .sum()
                        .sort_values(ascending=False)
                        .reset_index()
                    )
                    top_xg_players.columns = ['Player', 'Team', 'Total xG']

                    # Update the top players table dynamically
                    with top_players_placeholder.container():
                        st.write("### Top Players by xG")
                        st.write("""
                        ### Description of the Added Feature: Top Players by xG

                        We have implemented a dynamic visualization that identifies and updates the top players with the highest expected goals (xG) during the game. This feature processes live game data and aggregates xG values for each player in real-time, showing their total xG alongside their respective teams. 

                        The table updates dynamically as new events are streamed, ensuring that users always have the most accurate and up-to-date information about player performance. This functionality provides insights into individual contributions during the game, which can be valuable for analysts, fans, and coaches.

                        The implementation utilizes placeholders in Streamlit to replace old data with new updates, making it seamless and efficient.
                        """)

                        st.write(top_xg_players.head(10))

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
