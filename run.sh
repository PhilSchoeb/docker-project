#!/bin/bash

# Environment variables
PORT="8000"
WANDB_API_KEY="YOUR_WANDB_API_KEY"
WANDB_ORG="IFT6758-2024-A05"

# Image tag
TAG="latest"

# Exit on error
set -e

# Colors for the terminal
YELLOW='\033[1;33m'
GREEN='\033[0;32m'
NO_COLOR='\033[0m'

echo -e "${YELLOW}Stop previous docker images (if any)${NO_COLOR}"
docker stop ift6758-serving || true

echo -e "${YELLOW}Run the docker images${NO_COLOR}"
docker run \
  --rm \
  -d \
  -p ${PORT}:8000 \
  -e WANDB_API_KEY=${WANDB_API_KEY} \
  -e WANDB_ORG=${WANDB_ORG} \
  --name ift6758-serving \
  ift6758/serving:${TAG}

echo -e "${GREEN}Serving the model at http://localhost:${PORT}${NO_COLOR}"

