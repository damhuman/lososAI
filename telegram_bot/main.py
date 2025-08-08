import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from config import BOT_TOKEN
from bot.handlers import router

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

# Global bot instance for handlers
bot = None


async def main():
    """Main bot function"""
    # Initialize bot and dispatcher
    global bot  # Make bot accessible from handlers
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher(storage=MemoryStorage())
    
    # Add middleware to log all messages
    @dp.message.middleware()
    async def log_messages(handler, event, data):
        logger.info(f"📨 Received message: {event}")
        return await handler(event, data)
    
    # Include routers
    dp.include_router(router)
    
    # Log startup
    logger.info("Starting Seafood Store Bot...")
    
    try:
        # Start polling
        await dp.start_polling(bot)
    except Exception as e:
        logger.error(f"Error starting bot: {e}")
    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())