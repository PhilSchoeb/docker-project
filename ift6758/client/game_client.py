import json
import requests
import pandas as pd
import logging
import sys 
import os 
import time
import streamlit as st
from . import ServingClient

# Add the parent directory to the path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from data.ApiClient import ApiClient
from data.DataTransformer import DataTransformer
from features.preprocess_advanced import preprocess_advanced

logger = logging.getLogger(__name__)

class GameClient:
    def __init__(self, ip: str = "0.0.0.0", port: int = 5000, serving_client: ServingClient = ServingClient(ip="127.0.0.1", port=8000)):
        self.base_url = f"http://{ip}:{port}"
        logger.info(f"Initializing client; base URL: {self.base_url}")

        # any other potential initialization
        # Initialize an ApiClient instance
        self.api_client = ApiClient()
        self.data_transformer = DataTransformer()
        self.serving_client = serving_client

    def download_live_game_events(self, game_id: str = None, features: list =  None):
        """
        Continuously download events for a live game, process only new events (flattening of the data and addition of features),
        and yield updated data as it is collected. Check if new data has been added every chosen time interval (default = 10 seconds.

        Returns the updated dataframe with processed events everytime there were new events added.
        """

        self.game_id = game_id
        if features == None:
            features = ["goal_distance"]

        # Fetch initial game state to check if the game is live
        game_data = self.api_client.get_game_data(self.game_id)
        is_live = game_data.get("gameState")

        # Checks if game is live
        if is_live not in ["LIVE", "CRIT"]:
            st.error(f"Game need to be live to calculate predictions. Current game state is {is_live}.")
        else:
            st.info(f"Game is live!")

        # is_live = "LIVE"        # If you want to test the client and the app with games not live you can unccomment this
            
        # Initialize expected goals at 0
        xG_home, xG_away = 0, 0

        # Tracker for processed event ids
        processed_events = set()  

        while is_live in ["LIVE", "CRIT"]:
            try:
                # Fetch current game data
                game_data = self.api_client.get_game_data(self.game_id)

                period = game_data['displayPeriod']
                time_left = game_data['clock']['secondsRemaining']
                home_score = game_data['homeTeam']['score']
                away_score = game_data['awayTeam']['score']
                home_id = game_data['homeTeam']['id']
                away_id = game_data['awayTeam']['id']

                # Flatten the game data into a DataFrame
                raw_data = pd.DataFrame(self.data_transformer.flatten_game(game_data, play_types="shot-on-goal"))

                # Identify new events that haven't been processed yet
                new_events = raw_data[~raw_data["event_idx"].isin(processed_events)]

                if not new_events.empty:

                    # Add new events features
                    new_events = preprocess_advanced(new_events)

                    # Update the tracker with processed event indices
                    processed_events.update(new_events["event_idx"]) 

                    print(f"Processed {len(new_events)} new events for game {self.game_id} at {time.ctime()}")

                    # Selecting for features of interest for model 
                    events_features = new_events[features]

                    # Make predictions on new events for features used by model
                    events_predictions = self.serving_client.predict(events_features)
                    
                    # Combine predictions df with all features 
                    events_predictions = pd.merge(new_events, events_predictions, left_index=True, right_index=True, how="inner")

                    #Expected goals
                    xG_home = xG_home + events_predictions.loc[events_predictions["event_owner_team_id"] == home_id, "goal_prob"].sum()
                    xG_away = xG_away + events_predictions.loc[events_predictions["event_owner_team_id"] == away_id, "goal_prob"].sum()

                    # Returns dict with new_events, time, period, scores and id of teams for estimating xG
                    yield {'new_events':events_predictions,
                    'live_data':
                    {'time':time_left,
                    'period':period,
                    'home_score': home_score,
                    'away_score': away_score,
                    'xG_home': xG_home,
                    'xG_away': xG_away}}

                else:
                    print("No new events to process.")

                    # Returns dict with new_events, time, period, scores and id of teams for estimating xG
                    yield {'new_events':None,
                    'live_data':
                    {'time':time_left,
                    'period':period,
                    'home_score': home_score,
                    'away_score': away_score,
                    'xG_home': xG_home,
                    'xG_away': xG_away}}


                # Check if the game is still live
                game_data = self.api_client.get_game_data(self.game_id)
                is_live = game_data.get("gameState")

            except Exception as e:
                print(f"Error while fetching data: {e}")
                break

        print("Game is no longer live. No further data will be collected.")
        return

    def download_live_game_information(self, game_id: str = None):
        """
        Returns home and away team names 
        """

        self.game_id = game_id

        # Fetch game data
        game_data = self.api_client.get_game_data(self.game_id)
        home_team = game_data['homeTeam']['commonName']['default']
        away_team = game_data['awayTeam']['commonName']['default']

        return {'home_team': home_team, 'away_team':away_team}

        