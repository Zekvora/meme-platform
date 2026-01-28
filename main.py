"""
MemeMakerBot - Main Entry Point
"""
import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

from config import BOT_TOKEN, LOG_LEVEL
from database import init_db
import database_new as db_new
from handlers import user_router, admin_router
from middlewares import RateLimitMiddleware, UserTrackingMiddleware, ErrorLoggingMiddleware


# Configure logging
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL, logging.INFO),
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger(__name__)


async def main():
    """Main function."""
    logger.info("Starting MemeMakerBot...")
    
    # Initialize databases
    await init_db()
    await db_new.init_db()
    logger.info("Databases initialized")
    
    # Create bot and dispatcher
    bot = Bot(
        token=BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    dp = Dispatcher(storage=MemoryStorage())
    
    # Register middlewares
    dp.message.middleware(RateLimitMiddleware())
    dp.message.middleware(UserTrackingMiddleware())
    dp.message.middleware(ErrorLoggingMiddleware())
    dp.callback_query.middleware(RateLimitMiddleware())
    dp.callback_query.middleware(UserTrackingMiddleware())
    dp.callback_query.middleware(ErrorLoggingMiddleware())
    
    # Register routers
    dp.include_router(admin_router)  # Admin first (for /admin command)
    dp.include_router(user_router)
    
    logger.info("Bot is ready!")
    
    # Start polling
    await dp.start_polling(bot, allowed_updates=["message", "callback_query"])


if __name__ == "__main__":
    asyncio.run(main())
