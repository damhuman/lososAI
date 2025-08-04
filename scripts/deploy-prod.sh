#!/bin/bash

# Production deployment script
# Usage: ./scripts/deploy-prod.sh

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}Starting production deployment...${NC}"

# Check if .env file exists
if [ ! -f .env ]; then
    echo -e "${RED}Error: .env file not found. Please create it from .env.template${NC}"
    exit 1
fi

# Login to DigitalOcean Container Registry
echo -e "${YELLOW}Logging in to DigitalOcean Container Registry...${NC}"
echo "Please ensure you're logged in to DigitalOcean Container Registry:"
echo "doctl registry login"
echo "Or use: docker login registry.digitalocean.com"
echo ""

# Pull latest images
echo -e "${YELLOW}Pulling latest images...${NC}"
docker-compose -f docker-compose.prod.yml pull

# Stop existing containers
echo -e "${YELLOW}Stopping existing containers...${NC}"
docker-compose -f docker-compose.prod.yml down

# Start production environment
echo -e "${YELLOW}Starting production environment...${NC}"
docker-compose -f docker-compose.prod.yml up -d

# Wait for services to be ready
echo -e "${YELLOW}Waiting for services to be ready...${NC}"
sleep 10

# Check service status
echo -e "${YELLOW}Checking service status...${NC}"
docker-compose -f docker-compose.prod.yml ps

echo -e "${GREEN}Production deployment completed!${NC}"
echo ""
echo -e "${GREEN}Services available at:${NC}"
echo "- Main App: http://localhost:80"
echo "- Admin Panel: http://localhost:80/admin"
echo "- API Docs: http://localhost:8000/docs"
echo "- HTTPS: https://localhost:443 (if SSL configured)"