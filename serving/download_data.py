import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from ift6758.data import fetch_all_seasons_games_data

# Download the play by play data for every season
fetch_all_seasons_games_data()