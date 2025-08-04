# Docker Production Deployment

This guide explains how to build and deploy the Losos Seafood Store application using Docker containers with DigitalOcean Container Registry.

## Files Overview

### Docker Compose Files
- `docker-compose.yml` - Development environment
- `docker-compose.build.yml` - Build and push images to registry
- `docker-compose.prod.yml` - Production deployment using registry images

### Dockerfiles
- `docker/backend.Dockerfile` - FastAPI backend (multi-stage production build)
- `docker/bot.Dockerfile` - Telegram bot (multi-stage production build)
- `docker/admin-react.prod.Dockerfile` - React admin panel (multi-stage with nginx)
- `docker/nginx/Dockerfile` - Nginx reverse proxy

### Scripts
- `scripts/build-and-push.sh` - Build and push all images to registry
- `scripts/deploy-prod.sh` - Deploy production environment

## Registry Configuration

The project is configured to use DigitalOcean Container Registry with namespace `losos`:

```
registry.digitalocean.com/losos/backend:latest
registry.digitalocean.com/losos/telegram-bot:latest
registry.digitalocean.com/losos/admin-react:latest
registry.digitalocean.com/losos/nginx:latest
```

## Quick Start

### 1. Build and Push Images

```bash
# Make sure you have the registry authentication configured
./scripts/build-and-push.sh
```

This script will:
- Login to DigitalOcean Container Registry
- Build all Docker images with production optimizations
- Push images to the registry

### 2. Deploy to Production

```bash
# Create .env file from template first
cp .env.template .env
# Edit .env with your production values

# Deploy production environment
./scripts/deploy-prod.sh
```

This script will:
- Login to the registry
- Pull latest images
- Stop existing containers
- Start production environment
- Show service status

## Manual Commands

### Build Images
```bash
docker-compose -f docker-compose.build.yml build
```

### Push Images
```bash
docker-compose -f docker-compose.build.yml push
```

### Deploy Production
```bash
docker-compose -f docker-compose.prod.yml up -d
```

### View Logs
```bash
docker-compose -f docker-compose.prod.yml logs -f
```

### Stop Production
```bash
docker-compose -f docker-compose.prod.yml down
```

## Production Features

### Security Enhancements
- Multi-stage builds to reduce image size
- Non-root users in containers
- Security headers in nginx
- Separate networks for services

### Performance Optimizations
- Multi-stage builds with build cache
- Nginx serving static assets
- React production build with asset caching
- Health checks for all services

### Service Configuration
- **Database**: PostgreSQL 15 with health checks
- **Cache**: Redis 7 Alpine with persistence
- **Backend**: FastAPI with Uvicorn (production mode)
- **Bot**: Telegram bot with restart policies
- **Admin**: React SPA served by nginx
- **Proxy**: Nginx with SSL support and reverse proxy

## Environment Variables

Make sure to configure these production environment variables in `.env`:

```env
# Required
SECRET_KEY=your-secret-key
TELEGRAM_BOT_TOKEN=your-bot-token
ADMIN_PASSWORD=secure-admin-password
WEB_APP_URL=https://yourdomain.com

# Database
POSTGRES_USER=seafood_user
POSTGRES_PASSWORD=secure-db-password
POSTGRES_DB=seafood_store

# S3/Spaces (for file uploads)
S3_ENDPOINT_URL=https://fra1.digitaloceanspaces.com
S3_ACCESS_KEY_ID=your-spaces-key
S3_SECRET_ACCESS_KEY=your-spaces-secret
S3_BUCKET_NAME=your-bucket-name
S3_REGION=fra1
S3_PUBLIC_URL=https://your-bucket.fra1.digitaloceanspaces.com
```

## Network Configuration

Production deployment creates a custom bridge network `losos-network` for service communication with proper isolation.

## SSL/HTTPS

For HTTPS support:
1. Place SSL certificates in `docker/nginx/ssl/`
2. Update nginx configuration if needed
3. Ensure `WEB_APP_URL` uses HTTPS (required for Telegram Web Apps)

## Monitoring

Check service health:
```bash
docker-compose -f docker-compose.prod.yml ps
docker-compose -f docker-compose.prod.yml logs -f [service-name]
```

## Troubleshooting

### Registry Login Issues
- Verify DigitalOcean Container Registry credentials
- Check `.dockerconfigjson` file exists and has correct auth token

### Build Failures
- Ensure all required files exist in respective directories
- Check Dockerfile paths in docker-compose.build.yml

### Deployment Issues
- Verify `.env` file has all required variables
- Check network connectivity to registry
- Ensure ports are not in use by other services