import pandas as pd
from ift6758.client.serving_client import ServingClient
from ift6758.client.game_client import GameClient

# Initialize clients
game_client = GameClient(ip="127.0.0.1", port=8000)
serving_client = ServingClient(ip="127.0.0.1", port=8000)

# Specify the features required for the model
required_features = ["goal_distance"] 

try:
    # Fetch live game events and process them dynamically
    for events_df in game_client.download_live_game_events(interval=10):

        # Filter only the columns required for prediction
        prediction_data = events_df[required_features]

        # Make predictions on currently loaded events using the ServingClient
        predictions = serving_client.predict(prediction_data)
        
        # Output enriched data or save it for further analysis
        print("Enriched data with predictions:")
        print(enriched_data.head())

except Exception as e:
    print(f"An error occurred during processing: {e}")
