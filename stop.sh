#!/bin/bash

# Exit on error
set -e

# Container options
NAME_SERVING="ift6758-serving"
NAME_STREAMLIT="ift6758-streamlit"
NETWORK_NAME="ift6758-network"

# Colors for the terminal
YELLOW='\033[1;33m'
GREEN='\033[0;32m'
NO_COLOR='\033[0m'

echo -e "${YELLOW}Stop docker containers${NO_COLOR}"
docker stop ${NAME_SERVING} || true
docker stop ${NAME_STREAMLIT} || true

echo -e "${YELLOW}Remove docker network${NO_COLOR}"
docker network rm ${NETWORK_NAME} || true

echo -e "${GREEN}All containers have been stopped and network removed${NO_COLOR}"

