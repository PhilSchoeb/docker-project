#!/bin/bash

# Exit on error
set -e

# Container options
PORT_SERVING="8000"
PORT_STREAMLIT="8501"
TAG="latest"
NAME_SERVING="ift6758-serving"
NAME_STREAMLIT="ift6758-streamlit"

# Colors for the terminal
YELLOW='\033[1;33m'
PURPLE='\033[0;35m'
GREEN='\033[0;32m'
NO_COLOR='\033[0m'

# Load .env file if it exists
# Allows to set the WANDB_API_KEY and WANDB_ORG without exposing them in the script
if [ -f .env ] ; then
  echo -e "${PURPLE}Loading environment variables from .env file${NO_COLOR}"
  export $(cat .env | xargs)
fi

echo -e "${YELLOW}Stop previous docker containers (if any)${NO_COLOR}"
docker stop ${NAME_SERVING} || true
docker stop ${NAME_STREAMLIT} || true

echo -e "${YELLOW}Run the docker containers${NO_COLOR}"
docker run \
  --rm \
  -d \
  -p ${PORT_SERVING}:8000 \
  -e WANDB_API_KEY=${WANDB_API_KEY} \
  -e WANDB_ORG=${WANDB_ORG} \
  --name ${NAME_SERVING} \
  ift6758/serving:${TAG}

docker run \
  --rm \
  -d \
  -p ${PORT_STREAMLIT}:8501 \
  -e GAME_CLIENT_HOST="127.0.0.1" \
  -e GAME_CLIENT_PORT=${PORT_SERVING} \
  -e SERVING_CLIENT_HOST="127.0.0.1" \
  -e SERVING_CLIENT_PORT=${PORT_SERVING} \
  --name ${NAME_STREAMLIT} \
  ift6758/streamlit:${TAG}

echo -e "${GREEN}Serving the model at http://localhost:${PORT_SERVING}${NO_COLOR}"
echo -e "${GREEN}Streamlit app running at http://localhost:${PORT_STREAMLIT}${NO_COLOR}"

