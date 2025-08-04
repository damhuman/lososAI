#!/bin/bash

# Build and push script for DigitalOcean Container Registry
# Usage: ./scripts/build-and-push.sh

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}Starting build and push process...${NC}"

# Login to DigitalOcean Container Registry
echo -e "${YELLOW}Logging in to DigitalOcean Container Registry...${NC}"
echo "Please ensure you're logged in to DigitalOcean Container Registry:"
echo "doctl registry login"
echo "Or use: docker login registry.digitalocean.com"
echo ""

# Build all images
echo -e "${YELLOW}Building Docker images...${NC}"
docker-compose -f docker-compose.build.yml build --no-cache

# Push all images
echo -e "${YELLOW}Pushing images to registry...${NC}"
docker-compose -f docker-compose.build.yml push

echo -e "${GREEN}Build and push completed successfully!${NC}"

# Show pushed images
echo -e "${YELLOW}Pushed images:${NC}"
echo "- registry.digitalocean.com/losos/backend:latest"
echo "- registry.digitalocean.com/losos/telegram-bot:latest"
echo "- registry.digitalocean.com/losos/admin-react:latest"

echo ""
echo -e "${GREEN}You can now deploy using:${NC}"
echo "docker-compose -f docker-compose.prod.yml up -d"