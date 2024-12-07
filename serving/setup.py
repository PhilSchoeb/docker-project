import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from ift6758.data import load_events_dataframe
from ift6758.features import load_advanced_dataframe
import pandas as pd
import numpy as np

# Run after the data has been downloaded

# Try loading the dataframe of events for 2022 (we chose 2022 because this data was not used for training on our simple
# models but you can change to whatever season
problem = False
try:
    df_2022 = load_events_dataframe(2022)
except Exception as e:
    print("Could not load the dataframe")
    print(str(e.message))
    problem = True

# Store the data in this folder if it was loaded successfully
if not problem:
    df = df_2022[["goal_distance", "goal_angle", "is_goal"]]
    df.to_csv("./test_data_2022.csv")

