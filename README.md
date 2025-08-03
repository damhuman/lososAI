# 🐟 Seafood Store - Telegram Mini App

A complete Telegram Mini App for a seafood store built with Python (FastAPI), vanilla JavaScript, and PostgreSQL.

## 🏗️ Architecture

```
bot/
├── backend/           # FastAPI backend API
├── frontend/          # Telegram Web App (SPA)
├── telegram_bot/      # Telegram bot (aiogram)
├── admin/            # Flask admin panel
├── docker/           # Docker configurations
└── tests/            # Test suites
```

## 🚀 Features

### 🛒 Customer Features
- **Product Catalog**: Browse 4 categories (Salmon, Shellfish, Tom Yum kits, Caviar)
- **Product Details**: View product info, select packaging, adjust quantities
- **Shopping Cart**: LocalStorage-based cart with persistent state
- **Order Flow**: Select delivery district and time slot
- **Promo Codes**: Apply discount codes and Gold client identification
- **Telegram Integration**: Full Web App API integration with haptic feedback

### 👨‍💼 Admin Features
- **Order Management**: View, confirm, and cancel orders
- **Product Management**: Add/edit products, manage inventory
- **User Management**: View customer data, manage Gold clients
- **Promo Code Management**: Create and manage discount codes
- **District Management**: Configure delivery areas

### 🤖 Bot Features
- **Web App Launch**: Single button to open the store
- **Order Processing**: Receive and forward orders to admin
- **Admin Notifications**: Real-time order alerts with action buttons
- **Ukrainian Language**: Full Ukrainian interface

## 🛠️ Technology Stack

### Backend
- **FastAPI**: High-performance async API framework
- **SQLAlchemy 2.0**: Modern async ORM
- **PostgreSQL**: Primary database
- **Redis**: Caching and session storage
- **Alembic**: Database migrations
- **Pydantic**: Data validation and serialization

### Frontend
- **Vanilla JavaScript**: ES6+ with modules
- **Telegram Web App API**: Native Telegram integration
- **CSS3**: Responsive design with Telegram theming
- **LocalStorage**: Client-side cart persistence

### Bot
- **aiogram 3.x**: Modern async Telegram bot framework
- **Python 3.11**: Latest Python features

### Admin Panel
- **Flask**: Lightweight web framework
- **Flask-Admin**: Admin interface
- **Bootstrap 4**: UI framework

### Infrastructure
- **Docker Compose**: Multi-container orchestration
- **Nginx**: Reverse proxy and static file serving
- **SSL/TLS**: Required for Telegram Web Apps

## 📋 Prerequisites

- Docker and Docker Compose
- SSL certificate (required for Telegram Web Apps)
- Telegram Bot Token (from [@BotFather](https://t.me/botfather))
- Domain name or ngrok for HTTPS

## 🚀 Quick Start

### 1. Clone and Setup

```bash
git clone <repository-url>
cd bot
cp .env.template .env
```

### 2. Configure Environment

Edit `.env` file:

```env
# Required
SECRET_KEY=your-secret-key-here
TELEGRAM_BOT_TOKEN=your-bot-token-from-botfather
ADMIN_PASSWORD=your-admin-password
WEB_APP_URL=https://your-domain.com/webapp

# Optional
ADMIN_CHAT_ID=your-telegram-chat-id-for-notifications
```

### 3. Start Services

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f
```

### 4. Initialize Database

```bash
# Run migrations
docker-compose exec backend alembic upgrade head

# Seed test data
docker-compose exec backend python seed_data.py
```

### 5. Configure Bot

1. Set up webhook URL with BotFather:
   ```
   /setwebapp
   Bot: @your_bot_name
   URL: https://your-domain.com/webapp
   ```

2. Set menu button (optional):
   ```
   /setmenubutton
   Bot: @your_bot_name
   Button text: 🛒 Магазин
   Web App URL: https://your-domain.com/webapp
   ```

## 🔗 Service URLs

- **Web App**: https://your-domain.com/webapp
- **API Docs**: http://localhost:8000/docs
- **Admin Panel**: http://localhost:5000
- **Bot**: [@your_bot_name](https://t.me/your_bot_name)

## 🧪 Testing

### Backend Tests
```bash
# Run backend tests
docker-compose exec backend pytest

# With coverage
docker-compose exec backend pytest --cov=app tests/
```

### Frontend Tests
```bash
# Run frontend tests (if implemented)
cd frontend && npm test
```

### Manual Testing
1. Start services with test data
2. Open admin panel and verify products
3. Test bot with `/start` command
4. Complete an order flow
5. Check admin notifications

## 📝 API Endpoints

### Public Endpoints
- `GET /api/v1/categories` - List categories
- `GET /api/v1/categories/{id}/products` - Category products
- `GET /api/v1/products/{id}` - Product details
- `GET /api/v1/districts` - Delivery districts
- `POST /api/v1/promo/validate` - Validate promo code

### Authenticated Endpoints (require Telegram auth)
- `POST /api/v1/orders` - Create order
- `GET /api/v1/orders` - User's orders
- `GET /api/v1/orders/{id}` - Order details

## 🔐 Authentication

The app uses Telegram Web App initData for authentication:
1. Frontend sends initData in Authorization header
2. Backend validates using HMAC-SHA256
3. User is created/updated automatically
4. No traditional login required

## 🌐 Deployment

### Production Checklist
- [ ] SSL certificate configured
- [ ] Environment variables set
- [ ] Database backups enabled
- [ ] Log monitoring setup
- [ ] Bot webhook configured
- [ ] Admin credentials secured
- [ ] Rate limiting enabled

### Docker Production
```bash
# Production compose
docker-compose -f docker-compose.prod.yml up -d
```

### Manual Deployment
1. Set up PostgreSQL and Redis
2. Configure Nginx with SSL
3. Deploy each service separately
4. Set up process management (systemd/supervisor)

## 🎨 Customization

### Adding New Products
1. Use admin panel or seed script
2. Add product images to `/static/images/`
3. Configure packages and pricing

### Styling
- Edit `frontend/webapp/css/styles.css`
- Telegram theme colors auto-applied
- Responsive design included

### Adding Features
- Backend: Add new endpoints in `backend/app/api/endpoints/`
- Frontend: Extend JavaScript modules
- Bot: Add handlers in `telegram_bot/bot/handlers.py`

## 🐛 Troubleshooting

### Common Issues

**Bot not responding**
- Check bot token
- Verify webhook URL is HTTPS
- Check logs: `docker-compose logs telegram-bot`

**Web App not loading**
- Ensure SSL certificate is valid
- Check CORS settings
- Verify WEB_APP_URL in environment

**Database connection errors**
- Check PostgreSQL is running
- Verify database credentials
- Run migrations: `alembic upgrade head`

**Orders not showing in admin**
- Check admin chat ID
- Verify bot can send messages
- Check order creation logs

### Logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend
docker-compose logs -f telegram-bot
```

## 🤝 Contributing

1. Fork the repository
2. Create feature branch
3. Add tests for new features
4. Ensure all tests pass
5. Submit pull request

## 📄 License

MIT License - see LICENSE file for details.

## 🆘 Support

For issues and questions:
1. Check troubleshooting section
2. Review logs for errors
3. Create GitHub issue with details
4. Include environment info and error messages

---

**🐟 Happy seafood selling!** 🦐