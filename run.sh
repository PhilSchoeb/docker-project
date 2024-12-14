#!/bin/bash

# Exit on error
set -e

# Container options
PORT="8000"
TAG="latest"
NAME_SERVING="ift6758-serving"

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

echo -e "${YELLOW}Run the docker containers${NO_COLOR}"
docker run \
  --rm \
  -d \
  -p ${PORT}:8000 \
  -e WANDB_API_KEY=${WANDB_API_KEY} \
  -e WANDB_ORG=${WANDB_ORG} \
  --name ${NAME_SERVING} \
  ift6758/serving:${TAG}

echo -e "${GREEN}Serving the model at http://localhost:${PORT}${NO_COLOR}"

