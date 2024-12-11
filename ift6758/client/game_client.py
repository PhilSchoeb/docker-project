import json
import requests
import pandas as pd
import logging
import sys 
import os 

# Add the parent directory to the path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from data.ApiClient import ApiClient
from data.DataTransformer import DataTransformer




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


    def download_events(self) -> pd.DataFrame:

        '''

        Download events associated with a game based on game_id, transform it into
        raw data and select for columns of interest.

        '''

        # Download events of a single game as a json
        game_json = []
        game_json.append(self.api_client.get_game_data(self.game_id))

        # Get raw data from json
        raw_game_data = self.data_transformer.flatten_raw_data_as_dataframe(games = game_json, play_types=None)

        game_data = raw_game_data[["game_id","event_idx","is_empty_net","is_goal","goal_distance","goal_angle"]]

        print(game_data)

        return(None)

