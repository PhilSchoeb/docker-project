"""
If you are in the same directory as this file (app.py), you can run run the app using gunicorn:
    
    $ gunicorn --bind 127.0.0.1:8000 app:app
    
You can then access the app logs at : http://127.0.0.1:8000/logs

gunicorn can be installed via:

    $ pip install gunicorn

"""
import os
from pathlib import Path
import logging
from flask import Flask, jsonify, request, abort
import pandas as pd
import numpy as np
import sklearn
import pandas as pd
import joblib
import wandb
import sys
import json
# Add the parent directory to the system path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import ift6758

# Wandb configuration
WANDB_ORG = os.environ.get("WANDB_ORG", "IFT6758-2024-A05")
LOG_FILE = os.environ.get("FLASK_LOG", "flask.log")
open(LOG_FILE, 'w').close()  # Empty log file from previous application runs
app = Flask(__name__)
model = None

# For before_first_request
def load_default_model():
    global model
    model_path = os.path.join(os.path.dirname(__file__), "./models/goal_distance_regression.joblib")
    try:
        model = joblib.load(model_path)
    except Exception as e:
        print(f"Could not load model at path : {model_path}. Error : {str(e)}")
    app.logger.info("Loaded default model (goal_distance_regression.joblib)")
    return

# Replacement for before_first_request
with app.app_context():
    logging.basicConfig(filename=LOG_FILE, level=logging.INFO)
    app.logger.info('Started before_first_request')
    load_default_model()  # Default model loaded
    app.logger.info('Finished before_first_request')


@app.route("/logs", methods=["GET"])
def logs():
    """Reads data from the log file and returns them as the response"""
    
    # TODO: read the log file specified and return the data
    f = open(LOG_FILE, "r")
    content = f.read()

    response = content.split("\n")
    if response[-1] == "":
        clean_repsonse = response[:-1]
        assert len(clean_repsonse) == len(response) - 1, "Failed removal of last empty element after logs reading"
        response = clean_repsonse
    return jsonify(response)  # response must be json serializable!


@app.route("/download_registry_model", methods=["POST"])
def download_registry_model():
    """
    Handles POST requests made to http://IP_ADDRESS:PORT/download_registry_model

    The Wandb API key should be retrieved from the ${WANDB_API_KEY} environment variable. (??? not sure ???)

    Recommend (but not required) json with the schema:

        {
            project: (required),
            model: (required),
            version: (required),
            ... (other fields if needed) ...
        }
    
    """
    global model
    # Get POST json data
    json_input = request.get_json()[0]
    project_name = json_input["project"]
    model_name = json_input["model"]
    version = json_input["version"]
    app.logger.info("download_registry_model request started")
    app.logger.info(json_input)

    # TODO: check to see if the model you are querying for is already downloaded
    model_path = os.path.join(os.path.dirname(__file__), "./models/" + model_name + ".joblib")
    already_downloaded = os.path.isfile(model_path)

    # TODO: if yes, load that model and write to the log about the model change.  
    # eg: app.logger.info(<LOG STRING>)
    if already_downloaded:
        try:
            model = joblib.load(model_path)
        except Exception as e:
            print(f"Could not load already downloaded model : {model_name} at path : {model_path}. Error : {str(e)}")
        response = f"Model change to : {model_name} (without download)"

    
    # TODO: if no, try downloading the model: if it succeeds, load that model and write to the log
    # about the model change. If it fails, write to the log about the failure and keep the 
    # currently loaded model
    else:
        api = wandb.Api()
        project_path = f"{WANDB_ORG}/{project_name}"  # Maybe add https://wandb.ai/ before ?
        artifact_path = f"{project_path}/{model_name}:{version}"
        try:
            artifact = api.artifact(artifact_path)
            model_path = os.path.join(os.path.dirname(__file__), "./models/")
            artifact.download(model_path)
            model_path = os.path.join(os.path.dirname(__file__), "./models/" + model_name + ".joblib")
            model = joblib.load(model_path)
            response = f"Model change to : {model_name} (with download)"
        except Exception as e:
            print(f"Error, could not access, download or load the model : {model_name}. Error : {str(e)}")
            response = f"Failure to change model to : {model_name}"

    app.logger.info(response)
    response = [response]
    return jsonify(response)  # response must be json serializable!


@app.route("/predict", methods=["POST"])
def predict():
    """
    Handles POST requests made to http://IP_ADDRESS:PORT/predict

    Returns predictions
    """
    # Get POST json data
    json_input = request.get_json()
    app.logger.info("predict request started")
    app.logger.info(json_input)

    # Create a DataFrame from the input
    df = pd.DataFrame.from_dict(json_input)

    # Generate predictions using the model
    predictions = model.predict_proba(df)

    app.logger.info(f"Predictions: {predictions}")
    return jsonify(predictions.tolist())  # response must be json serializable!