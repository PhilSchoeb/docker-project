#!/bin/bash

# Define the tag for the image
TAG="latest"

# Exit on error
set -e

# Colors for the terminal
YELLOW='\033[1;33m'
GREEN='\033[0;32m'
NO_COLOR='\033[0m'

echo -e "${YELLOW}Building Serving image${NO_COLOR}"
docker build -t ift6758/serving:${TAG} -f Dockerfile.serving .

echo -e "${YELLOW}Building Streamlit image${NO_COLOR}"
#docker build -t ift6758/streamlit:${TAG} -f Dockerfile.streamlit .

echo -e "${GREEN}Done building images${NO_COLOR}"
