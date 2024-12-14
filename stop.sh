#!/bin/bash

# Exit on error
set -e

# Container options
NAME_SERVING="ift6758-serving"

# Colors for the terminal
YELLOW='\033[1;33m'
GREEN='\033[0;32m'
NO_COLOR='\033[0m'

echo -e "${YELLOW}Stop docker container${NO_COLOR}"
docker stop ${NAME_SERVING} || true

echo -e "${GREEN}Servers has been stopped${NO_COLOR}"

