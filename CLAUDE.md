# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a complete Telegram Mini App for a seafood store with a multi-service architecture:

- **Backend**: FastAPI application with async SQLAlchemy 2.0 and PostgreSQL
- **Frontend**: Vanilla JavaScript Telegram Web App (SPA)
- **Telegram Bot**: aiogram 3.x bot for order management
- **Admin Panel**: Flask-based administrative interface
- **Infrastructure**: Docker Compose orchestration with Nginx, Redis

## Development Commands

### Starting Services
```bash
# Start all services with Docker Compose
docker-compose up -d

# View logs for all services
docker-compose logs -f

# View logs for specific service
docker-compose logs -f backend
docker-compose logs -f telegram-bot
```

### Database Operations
```bash
# Run database migrations
docker-compose exec backend alembic upgrade head

# Create new migration
docker-compose exec backend alembic revision --autogenerate -m "description"

# Seed test data
docker-compose exec backend python seed_data.py
```

### Testing
```bash
# Run backend tests
docker-compose exec backend pytest

# Run tests with coverage
docker-compose exec backend pytest --cov=app tests/
```

### Development Workflow
```bash
# Backend development (auto-reload enabled)
docker-compose up backend

# Check API documentation
# Visit: http://localhost:8000/docs
```

## Architecture

### Service Communication
- **Backend API**: Port 8000, serves `/api/v1/*` endpoints and web app static files
- **Admin Panel**: Port 5001, connects directly to PostgreSQL
- **Telegram Bot**: Communicates with backend via `http://backend:8000/api/v1`
- **Nginx**: Port 8081 (HTTP) / 8444 (HTTPS), reverse proxy for all services

### Database Schema
Key models in `backend/app/db/models/`:
- `User`: Telegram users with gold status and cart persistence
- `Product`: Products with categories, packages, and pricing
- `Order`: Orders with items, districts, and delivery slots

### Authentication
Uses Telegram Web App initData validation:
- Frontend sends initData in Authorization header
- Backend validates using HMAC-SHA256 with bot token
- Users are auto-created/updated from Telegram data

### Frontend Architecture
- **SPA Router**: `js/router.js` handles client-side routing
- **API Client**: `js/api.js` centralized API communication
- **Cart Management**: `js/cart.js` with localStorage persistence
- **Telegram Integration**: `js/telegram.js` for Web App API

## Configuration

### Environment Setup
1. Copy `.env.template` to `.env`
2. Set required variables:
   - `SECRET_KEY`: Backend encryption key
   - `TELEGRAM_BOT_TOKEN`: From @BotFather
   - `ADMIN_PASSWORD`: Admin panel access
   - `WEB_APP_URL`: HTTPS URL for Telegram Web App

### SSL Requirements
Telegram Web Apps require HTTPS in production. Configure SSL certificates in `docker/nginx/ssl/` or use reverse proxy.

## Key Files

### Backend Core
- `backend/app/main.py`: FastAPI application setup
- `backend/app/core/config.py`: Pydantic settings with validation
- `backend/app/core/telegram_auth.py`: Telegram initData validation
- `backend/app/api/endpoints/`: API route handlers
- `backend/alembic/`: Database migration files

### Frontend
- `frontend/webapp/index.html`: SPA entry point
- `frontend/webapp/js/app.js`: Main application logic
- `frontend/webapp/css/styles.css`: Telegram-themed styling

### Bot
- `telegram_bot/bot/handlers.py`: Message and callback handlers
- `telegram_bot/bot/keyboards.py`: Inline keyboard definitions

## Development Notes

- Backend uses async/await throughout with SQLAlchemy 2.0 async session
- Frontend follows vanilla JS ES6+ modules pattern
- All services auto-reload in development mode
- Database migrations are automatically applied on backend startup
- Redis is used for caching and session storage
- Ukrainian language interface for bot and admin panel