import pandas as pd
from ift6758.client.serving_client import ServingClient
from ift6758.client.game_client import GameClient

# Initialize clients
game_client = GameClient(ip="127.0.0.1", port=8000)
serving_client = ServingClient(ip="127.0.0.1", port=8000)

# Specify the features required for the model
required_features = ["goal_distance"] 

try:

  for events_data in game_client.download_live_game_events(game_id = 2024020510, features = ["goal_distance"]):

            events_df = events_data['new_events']

            # Access the time and period data
            time_left = events_data['live_data']['time']
            period = events_data['live_data']['period']
            home_score = events_data['live_data']['home_score']
            away_score = events_data['live_data']['away_score']

            if events_df is not None:
                # Filter only the columns required for prediction
                predictions = events_df

                print(predictions)

except Exception as e:
    print(f"An error occurred during processing: {e}")

    # game_data = self.api_client.get_game_data(self.game_id)
    #     is_live = game_data.get("gameState")
    #         time_left = events_data['live_data']['time']
    #         period = events_data['live_data']['period']
    #         home_score = events_data['live_data']['home_score']
    #         away_score = events_data['live_data']['away_score']

    #         if events_df is not None:
    #             # Filter only the columns required for prediction
    #             prediction_data = events_df[required_features]

    #             # Make predictions on currently loaded events using the ServingClient
    #             predictions = serving_client.predict(prediction_data)

    #             # Update displayed dataframe
    #             all_data = pd.concat([all_data, predictions], ignore_index=True)

    #             # Calculate dynamic height based on the number of rows
    #             # total_height = len(all_data) * 36

