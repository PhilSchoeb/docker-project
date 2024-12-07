"""
If you are in the same directory as this file (app.py), you can run run the app using gunicorn:
    
    $ gunicorn --bind 0.0.0.0:<PORT> app:app

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
# Add the parent directory to the system path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import ift6758

logger = logging.getLogger(__name__)
LOG_FILE = os.environ.get("FLASK_LOG", "flask.log")
open(LOG_FILE, 'w').close()  # Empty log file from previous application runs
app = Flask(__name__)
model = None

# For before_first_request
def load_default_model():
    global model
    model_path = os.path.join(os.path.dirname(__file__), "./models/goal_distance_and_angle_regression.joblib")
    try:
        model = joblib.load(model_path)
    except:
        print("Error : could not load model at path : " + model_path)
    logger.info("Loaded default model (goal_distance_and_angle_regression.joblib)")
    return

# Replacement for before_first_request
with app.app_context():
    logging.basicConfig(filename=LOG_FILE, level=logging.INFO)
    logger.info('Started before_first_request')
    load_default_model()  # Default model loaded
    logger.info('Finished before_first_request')


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
    json = request.get_json()
    project_name = json[0]["project"]
    model_name = json[0]["model"]
    version = json[0]["version"]
    logger.info("download_registry_model request started")
    logger.info(json)

    # TODO: check to see if the model you are querying for is already downloaded
    model_path = os.path.join(os.path.dirname(__file__), "./models/" + model_name + ".joblib")
    already_downloaded = os.path.isfile(model_path)

    # TODO: if yes, load that model and write to the log about the model change.  
    # eg: app.logger.info(<LOG STRING>)
    if already_downloaded:
        try:
            model = joblib.load(model_path)
        except:
            print(f"Could not load already downloaded model : {model_name}")
        response = f"Model change to : {model_name} (without download)"

    
    # TODO: if no, try downloading the model: if it succeeds, load that model and write to the log
    # about the model change. If it fails, write to the log about the failure and keep the 
    # currently loaded model
    else:
        api = wandb.Api()
        project_path = f"IFT6758-2024-A05/{project_name}"  # Maybe add https://wandb.ai/ before ?
        artifact_path = f"{project_path}/{model_name}:{version}"
        try:
            artifact = api.artifact(artifact_path)
            model_path = os.path.join(os.path.dirname(__file__), "./models/")
            artifact.download(model_path)
            model_path = os.path.join(os.path.dirname(__file__), "./models/" + model_name + ".joblib")
            model = joblib.load(model_path)
            response = f"Model change to : {model_name} (with download)"
        except:
            print(f"Error, coould not access, download or load the model : {model_name}")
            response = f"Failure to change model to : {model_name}"

    logger.info(response)
    response = [response]
    return jsonify(response)  # response must be json serializable!


@app.route("/predict", methods=["POST"])
def predict():
    """
    Handles POST requests made to http://IP_ADDRESS:PORT/predict

    Returns predictions
    """
    # Get POST json data
    json = request.get_json()
    logger.info("predict request started")
    logger.info(json)
    
    df = pd.DataFrame.from_dict(json)
    X = df.to_numpy()
    assert np.shape(X)[1] == 1 or np.shape(X)[1] == 2
    predictions = model.predict_proba(X)
    response = json.dump(predictions.to_list())

    logger.info(response)
    return jsonify(response)  # response must be json serializable!
