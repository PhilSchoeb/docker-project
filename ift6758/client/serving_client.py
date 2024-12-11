import json
import requests
import pandas as pd
import logging


logger = logging.getLogger(__name__)


class ServingClient:
    def __init__(self, ip: str = "0.0.0.0", port: int = 5000, features=None):
        self.base_url = f"http://{ip}:{port}"
        logger.info(f"Initializing client; base URL: {self.base_url}")

        if features is None:
            features = ["goal_distance"]
        self.features = features

        # any other potential initialization

    def predict(self, X: pd.DataFrame) -> pd.DataFrame:
        """
        Formats the inputs into an appropriate payload for a POST request, and queries the
        prediction service. Retrieves the response from the server, and processes it back into a
        dataframe that corresponds index-wise to the input dataframe.
        
        Args:
            X (Dataframe): Input dataframe to submit to the prediction service.
        """

        url = f"{self.base_url}/predict"
        payload = X.to_dict(orient="records")  # Convert DataFrame to list of dicts
        
        try:
            # Send the POST request
            response = requests.post(url, json=payload)
            predictions = json.loads(response.text)  # Parse the stringified JSON response
            no_goal_prob = [pred[0] for pred in predictions]  # Extract probabilities of no_goal
            goal_prob = [pred[1] for pred in predictions]  # Extract probabilities that's it's a goal
            X_with_predictions = X.copy()  # Copy the original DataFrame and add probabilities columns to it
            X_with_predictions["no_goal_prob"] = no_goal_prob
            X_with_predictions["goal_prob"] = goal_prob
            
            return X_with_predictions

        except requests.exceptions.RequestException as e:
            logger.error(f"Error in predict: {e}")
            raise


    def logs(self) -> dict:
        """Get server logs"""

        url = f"{self.base_url}/logs"
    
        try:
            response = requests.get(url)
            logs = response.json()  
            return logs
        except requests.exceptions.RequestException as e:
            logger.error(f"Error in logs: {e}")
            raise


    def download_registry_model(self, workspace: str, model: str, version: str) -> dict:
        """
        Triggers a "model swap" in the service; the workspace, model, and model version are
        specified and the service looks for this model in the model registry and tries to
        download it. 

        See more here:

            https://www.comet.ml/docs/python-sdk/API/#apidownload_registry_model
        
        Args:
            workspace (str): The Comet ML workspace
            model (str): The model in the Comet ML registry to download
            version (str): The model version to download
        """
        
        url = f"{self.base_url}/download_registry_model"

        payload = [{
            "project": workspace,
            "model": model,
            "version": version,
        }]

        try:
            response = requests.post(url, json=payload)
            result = response.json()
            return result
        except requests.exceptions.RequestException as e:
            logger.error(f"Error in download_registry_model: {e}")
            raise
