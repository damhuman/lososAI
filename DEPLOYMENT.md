# Production Deployment Guide

This guide walks you through deploying the Losos Seafood Store to a production server.

## Prerequisites

- A server with Ubuntu 20.04+ (DigitalOcean Droplet, AWS EC2, etc.)
- A domain name (required for Telegram Web Apps)
- DigitalOcean Container Registry access
- Telegram Bot Token from @BotFather

## Step 1: Server Setup

### 1.1 Create a Server
- **DigitalOcean**: Create a Droplet (2GB RAM minimum)
- **AWS**: Launch an EC2 instance (t3.small or larger)
- **Any VPS**: Ensure Ubuntu 20.04+ with 2GB+ RAM

### 1.2 Connect to Server
```bash
ssh root@your-server-ip
# or
ssh ubuntu@your-server-ip
```

### 1.3 Install Dependencies
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.21.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Install Git and other tools
sudo apt install git nano curl -y

# Logout and login again for Docker group permissions
exit
ssh root@your-server-ip  # or ubuntu@your-server-ip
```

## Step 2: Clone and Configure

### 2.1 Clone Repository
```bash
# Clone your repository
git clone https://github.com/damhuman/losos-bot.git
cd losos-bot
```

### 2.2 Configure Environment
```bash
# Create environment file
cp .env.template .env
nano .env
```

**Required Environment Variables:**
```env
# Security
SECRET_KEY=your-very-secure-secret-key-here

# Telegram
TELEGRAM_BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz
ADMIN_CHAT_ID=your-telegram-user-id
WEB_APP_URL=https://yourdomain.com

# Database (change default passwords!)
POSTGRES_USER=seafood_user
POSTGRES_PASSWORD=your-secure-db-password
POSTGRES_DB=seafood_store

# Admin Panel
ADMIN_USERNAME=admin
ADMIN_PASSWORD=your-secure-admin-password

# File Storage (DigitalOcean Spaces or AWS S3)
S3_ENDPOINT_URL=https://fra1.digitaloceanspaces.com
S3_ACCESS_KEY_ID=your-spaces-access-key
S3_SECRET_ACCESS_KEY=your-spaces-secret-key
S3_BUCKET_NAME=your-bucket-name
S3_REGION=fra1
S3_PUBLIC_URL=https://your-bucket.fra1.digitaloceanspaces.com
```

## Step 3: SSL/Domain Setup

### 3.1 Point Domain to Server
- Add an A record pointing your domain to your server's IP
- Wait for DNS propagation (can take up to 24 hours)

### 3.2 Get SSL Certificate (Let's Encrypt)
```bash
# Install Certbot
sudo apt install certbot -y

# Get SSL certificate (replace yourdomain.com)
sudo certbot certonly --standalone -d yourdomain.com

# Copy certificates to nginx directory
sudo mkdir -p docker/nginx/ssl
sudo cp /etc/letsencrypt/live/yourdomain.com/fullchain.pem docker/nginx/ssl/
sudo cp /etc/letsencrypt/live/yourdomain.com/privkey.pem docker/nginx/ssl/
sudo chown -R $USER:$USER docker/nginx/ssl/
```

### 3.3 Update Nginx Configuration
```bash
nano docker/nginx/nginx.conf
```

Add SSL configuration:
```nginx
server {
    listen 443 ssl;
    server_name yourdomain.com;
    
    ssl_certificate /etc/nginx/ssl/fullchain.pem;
    ssl_certificate_key /etc/nginx/ssl/privkey.pem;
    
    # Your existing configuration...
}

server {
    listen 80;
    server_name yourdomain.com;
    return 301 https://$server_name$request_uri;
}
```

## Step 4: Deploy Application

### 4.1 Build Images (on your local machine first)
```bash
# From your local development machine
./scripts/build-and-push.sh
```

### 4.2 Deploy on Server
```bash
# On your server
./scripts/deploy-prod.sh
```

### 4.3 Verify Deployment
```bash
# Check running containers
docker-compose -f docker-compose.prod.yml ps

# Check logs
docker-compose -f docker-compose.prod.yml logs -f

# Check specific service logs
docker-compose -f docker-compose.prod.yml logs -f backend
```

## Step 5: Configure Telegram Bot

### 5.1 Set Webhook (optional, for webhook mode)
```bash
curl -X POST "https://api.telegram.org/bot<YOUR_BOT_TOKEN>/setWebhook" \
     -H "Content-Type: application/json" \
     -d '{"url": "https://yourdomain.com/api/v1/telegram/webhook"}'
```

### 5.2 Set Bot Commands
```bash
curl -X POST "https://api.telegram.org/bot<YOUR_BOT_TOKEN>/setMyCommands" \
     -H "Content-Type: application/json" \
     -d '{
       "commands": [
         {"command": "start", "description": "Запустити бота"},
         {"command": "menu", "description": "Переглянути меню"},
         {"command": "cart", "description": "Мій кошик"},
         {"command": "orders", "description": "Мої замовлення"}
       ]
     }'
```

## Step 6: Access Your Application

Once deployed, your application will be available at:
- **Main App**: https://yourdomain.com
- **Admin Panel**: https://yourdomain.com/admin
- **API Documentation**: https://yourdomain.com/docs

## Maintenance Commands

### Update Application
```bash
# Pull latest code
git pull origin main

# Rebuild and push images (from local machine)
./scripts/build-and-push.sh

# Deploy updates
./scripts/deploy-prod.sh
```

### View Logs
```bash
docker-compose -f docker-compose.prod.yml logs -f [service-name]
```

### Backup Database
```bash
docker-compose -f docker-compose.prod.yml exec db pg_dump -U seafood_user seafood_store > backup.sql
```

### Restore Database
```bash
docker-compose -f docker-compose.prod.yml exec -T db psql -U seafood_user seafood_store < backup.sql
```

## Troubleshooting

### Common Issues

**1. Docker permission denied**
```bash
sudo usermod -aG docker $USER
# Logout and login again
```

**2. Port already in use**
```bash
sudo netstat -tulpn | grep :80
sudo kill -9 <PID>
```

**3. SSL certificate issues**
```bash
sudo certbot renew --dry-run
sudo systemctl status certbot.timer
```

**4. Database connection issues**
- Check database credentials in `.env`
- Verify database container is running
- Check network connectivity between services

### Support

For issues:
1. Check logs: `docker-compose -f docker-compose.prod.yml logs -f`
2. Verify environment variables in `.env`
3. Ensure domain DNS is properly configured
4. Check SSL certificate validity

## Security Checklist

- [ ] Changed all default passwords
- [ ] SSL certificate installed and working
- [ ] Firewall configured (ports 80, 443, 22 only)
- [ ] Regular backups scheduled
- [ ] Monitoring set up
- [ ] Log rotation configured