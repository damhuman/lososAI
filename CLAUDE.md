# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a complete Telegram Mini App for a seafood store with a multi-service architecture:

- **Backend**: FastAPI application with async SQLAlchemy 2.0 and PostgreSQL
- **Frontend**: Vanilla JavaScript Telegram Web App (SPA)
- **Telegram Bot**: aiogram 3.x bot for order management
- **Admin Panel**: React-based administrative interface with TypeScript
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
docker-compose logs -f admin-react
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

# Admin panel development (hot reload enabled)
docker-compose up admin-react

# Check API documentation
# Visit: http://localhost:8000/docs

# Access admin panel
# Visit: http://localhost:8081/admin
```

## Architecture

### Service Communication
- **Backend API**: Port 8000, serves `/api/v1/*` endpoints and web app static files
- **React Admin Panel**: Port 3001, communicates with backend via `/api/v1/admin/*` endpoints
- **Telegram Bot**: Communicates with backend via `http://backend:8000/api/v1`
- **Nginx**: Port 8081 (HTTP) / 8444 (HTTPS), reverse proxy for all services

### Database Schema
Key models in `backend/app/db/models/`:
- `User`: Telegram users with gold status and cart persistence
- `Product`: Products with categories, packages, and pricing
- `Order`: Orders with items, districts, and delivery slots

### Authentication

**Telegram Web App (Customer Frontend):**
- Uses Telegram Web App initData validation
- Frontend sends initData in Authorization header
- Backend validates using HMAC-SHA256 with bot token
- Users are auto-created/updated from Telegram data

**Admin Panel:**
- Uses HTTP Basic Authentication
- Admin credentials stored in environment variables (`ADMIN_USERNAME`, `ADMIN_PASSWORD`)
- All admin API endpoints require Basic Auth header

### Frontend Architecture

**Customer Web App (Vanilla JS):**
- **SPA Router**: `js/router.js` handles client-side routing
- **API Client**: `js/api.js` centralized API communication
- **Cart Management**: `js/cart.js` with localStorage persistence
- **Telegram Integration**: `js/telegram.js` for Web App API

**Admin Panel (React + TypeScript):**
- **React Router**: Client-side routing with `basename="/admin"`
- **React Query**: Data fetching, caching, and synchronization
- **Ant Design**: UI component library with Ukrainian localization
- **TypeScript**: Type safety and better development experience
- **Axios**: HTTP client with automatic Basic Auth injection

## Configuration

### Environment Setup
1. Copy `.env.template` to `.env`
2. Set required variables:
   - `SECRET_KEY`: Backend encryption key
   - `TELEGRAM_BOT_TOKEN`: From @BotFather
   - `ADMIN_USERNAME`: Admin panel username (default: admin)
   - `ADMIN_PASSWORD`: Admin panel password
   - `WEB_APP_URL`: HTTPS URL for Telegram Web App
   - `S3_*`: S3/DigitalOcean Spaces credentials for file uploads

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

### Admin Panel
- `admin-panel/src/App.tsx`: Main React application with routing
- `admin-panel/src/pages/`: Page components (Dashboard, Products, Orders, etc.)
- `admin-panel/src/services/api.ts`: API client with Basic Auth
- `admin-panel/src/hooks/useAuth.tsx`: Authentication context and hooks
- `admin-panel/src/types/index.ts`: TypeScript type definitions

## Development Notes

- Backend uses async/await throughout with SQLAlchemy 2.0 async session
- Frontend follows vanilla JS ES6+ modules pattern
- All services auto-reload in development mode
- Database migrations are automatically applied on backend startup
- Redis is used for caching and session storage
- Ukrainian language interface for bot and admin panel

## Admin Panel

The admin panel is a React-based web application that provides comprehensive management capabilities for the seafood store.

### Access & Authentication
- **URL**: http://localhost:8081/admin (development)
- **Authentication**: HTTP Basic Auth
- **Default Credentials**: admin / admin123 (configurable via environment)

### Features & Functionality

**Dashboard:**
- Order statistics (total orders, revenue, average order value, orders by status)
- Product statistics (total products, categories, featured products, active products)
- User statistics (total users, active users, gold clients, blocked users)
- Recent orders overview

**Product Management:**
- Create, read, update, delete products
- Category assignment and management
- Package configuration (weight, price, availability)
- Image upload to S3/DigitalOcean Spaces
- Featured product designation
- Product activation/deactivation

**Category Management:**
- Create, edit, delete categories
- Category ordering and icons
- Category activation/deactivation

**Order Management:**
- View all orders with pagination and filtering
- Order status updates (pending, confirmed, preparing, delivered, cancelled)
- Order details with customer information and items
- Date range filtering
- Export orders to Excel format

**User Management:**
- View all registered users
- User status management (active, blocked)
- Gold status assignment
- User statistics and activity tracking

**Settings Management:**
- Delivery districts configuration
- Promo codes management (percentage and fixed amount discounts)
- Gold user promo codes

### Technical Implementation

**Frontend Stack:**
- React 18 with TypeScript
- Ant Design UI components
- React Router for client-side routing
- React Query for data fetching and caching
- Axios for HTTP requests with Basic Auth
- Day.js for date handling
- File-saver for Excel exports

**API Integration:**
- RESTful API communication with `/api/v1/admin/*` endpoints
- Automatic authentication header injection
- Error handling and loading states
- Real-time data synchronization

**Development Features:**
- Hot reload enabled for development
- TypeScript type safety
- Ukrainian localization
- Responsive design
- Form validation and error handling