import os
from dotenv import load_dotenv

load_dotenv()

# Bot configuration
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
WEB_APP_URL = os.getenv("WEB_APP_URL", "https://your-domain.com/webapp")
BACKEND_API_URL = os.getenv("BACKEND_API_URL", "http://backend:8000/api/v1")

# Admin configuration
ADMIN_CHAT_ID = os.getenv("ADMIN_CHAT_ID")  # Telegram chat ID for order notifications

if not BOT_TOKEN:
    raise ValueError("TELEGRAM_BOT_TOKEN must be set in environment")