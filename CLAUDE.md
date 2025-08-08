# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a complete Telegram Mini App for a seafood store with a multi-service architecture:

- **Backend**: FastAPI application with async SQLAlchemy 2.0 and PostgreSQL
- **Frontend**: Vanilla JavaScript Telegram Web App (SPA)
- **Telegram Bot**: aiogram 3.x bot for order management
- **Admin Panel**: React-based administrative interface with TypeScript
- **Infrastructure**: Docker Compose orchestration with Nginx, Redis

## 🔒 Security Requirements

**⚠️ CRITICAL: Always check for secrets before commits!**

### Pre-Commit Security Checklist
```bash
# 1. Check staged files for secrets
git diff --staged | grep -i -E "(password|secret|key|token|api_key|private|credential)"

# 2. Scan all files for hardcoded secrets  
grep -r -I --exclude-dir=node_modules --exclude-dir=.git -E "(password|secret|key|token).*=.*['\"][^'\"]{10,}" .

# 3. Check for environment files
find . -name "*.env*" -not -path "./.git/*"

# 4. Never commit these patterns:
# - Real API keys, tokens, passwords
# - Database credentials (except test/example)
# - SSH keys or certificates
# - .env files with real secrets
```

### Approved Test/Example Values
- `test_token`, `test_secret`, `test_password` ✅
- `admin123` (test credential being removed) ⚠️
- Environment templates with placeholder values ✅
- GitHub Actions with `secrets.GITHUB_TOKEN` ✅

### Secret Management
- **Production**: Use environment variables and secret management
- **Testing**: Use dedicated test tokens and mock values
- **CI/CD**: Store secrets in GitHub repository settings
- **Local Development**: Use `.env` files (never commit real values)

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

**⚠️ IMPORTANT: This project follows Test-Driven Development (TDD) practices. Always run tests before making changes and ensure new features have test coverage.**

```bash
# Run ALL tests (backend + frontend) with unified test runner
./test.sh

# Run only backend tests
./test.sh --backend-only
docker-compose exec backend pytest

# Run only frontend tests  
./test.sh --frontend-only

# Run with coverage reports
./test.sh --coverage
docker-compose exec backend pytest --cov=app tests/

# Frontend tests (from frontend/webapp/)
npm test
npm run test:coverage
```

#### Test Organization
- **Backend**: `backend/tests/` - pytest with async support (85/98 tests passing)
- **Frontend**: `frontend/webapp/__tests__/` - Jest with Telegram WebApp mocks (21/23 tests passing)
- **Integration**: End-to-end order flow and API tests
- **Coverage**: HTML reports generated in `backend/htmlcov/` and `frontend/webapp/coverage/`

#### TDD Workflow
1. **Red**: Write failing test for new feature
2. **Green**: Implement minimal code to pass test
3. **Refactor**: Clean up code while keeping tests green
4. **Repeat**: Continue cycle for each feature addition

#### GitHub Actions CI/CD
- **Continuous Integration**: Automated tests on every push/PR
- **Test Suite**: Backend (pytest) + Frontend (Jest) + Integration tests
- **Code Quality**: Formatting, linting, security scanning
- **Dependencies**: Automated updates via Dependabot
- **Deployment**: Automated deployment pipeline for releases

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
- Uses JWT authentication system
- Admin credentials validated against backend user database
- All admin API endpoints require JWT token in Authorization header

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
- **Axios**: HTTP client with automatic JWT token injection

## Configuration

### Environment Setup
1. Copy `.env.template` to `.env`
2. Set required variables:
   - `SECRET_KEY`: Backend encryption key
   - `TELEGRAM_BOT_TOKEN`: From @BotFather
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
- `admin-panel/src/services/api.ts`: API client with JWT authentication
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
- **Authentication**: JWT-based login system
- **Login**: Use admin credentials to obtain JWT token

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
- Automatic JWT token header injection
- Error handling and loading states
- Real-time data synchronization

**Development Features:**
- Hot reload enabled for development
- TypeScript type safety
- Ukrainian localization
- Responsive design
- Form validation and error handling