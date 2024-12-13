import json
import requests
import pandas as pd
import logging
import sys 
import os 
import time

# Add the parent directory to the path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from data.ApiClient import ApiClient
from data.DataTransformer import DataTransformer
from features.preprocess_advanced import preprocess_advanced




logger = logging.getLogger(__name__)

class GameClient:
    def __init__(self, ip: str = "0.0.0.0", port: int = 5000, game_id=None):
        self.base_url = f"http://{ip}:{port}"
        logger.info(f"Initializing client; base URL: {self.base_url}")

        if game_id is None:
            game_id = "2022030411"
        self.game_id = game_id


        # any other potential initialization
        # Initialize an ApiClient instance (you could pass cache here if needed)
        self.api_client = ApiClient()
        self.data_transformer = DataTransformer()


def download_live_game_events(self, interval: int = 10):
    """
    Continuously download events for a live game, process only new events (flattening of the data and addition of features),
    and yield updated data as it is collected. Check if new data has been added every chosen time interval (default = 10 seconds.

    Returns the updated dataframe with processed events everytime there were new events added.
    """

    # Fetch initial game state to check if the game is live
    game_data = self.api_client.get_game_data(self.game_id)
    is_live = game_data.get("gameState")

    if is_live != "ON":
        print("Game is not live, data will not be collected.")
        return

    all_events_data = []  # Collect processed events data frames
    processed_events = set()  # Tracker for processed event ids

    while is_live == "ON":
        try:
            # Fetch current game data
            game_data = self.api_client.get_game_data(self.game_id)

            # Flatten the game data into a DataFrame
            raw_data = pd.DataFrame(self.data_transformer.flatten_game(game_data, play_types=None))

            # Identify new events that haven't been processed
            new_events = raw_data[~raw_data["event_idx"].isin(processed_events)]

            if not new_events.empty:
                # Add new events features
                preprocessed_data = preprocess_advanced(new_events)

                # Add the preprocessed data to the collected data
                all_events_data.append(preprocessed_data)

                # Update the tracker with processed event indices
                processed_events.update(new_events["event_idx"])

                print(f"Processed {len(new_events)} new events for game {self.game_id} at {time.ctime()}")

                # Returns current data as DataFrame
                yield pd.concat(all_events_data, ignore_index=True)

            else:
                print("No new events to process.")

            # Wait for the specified time interval before the next fetch
            time.sleep(interval)

            # Check if the game is still live
            game_data = self.api_client.get_game_data(self.game_id)
            is_live = game_data.get("gameState")

        except Exception as e:
            print(f"Error while fetching data: {e}")
            break

    print("Game is no longer live. No further data will be collected.")
    return