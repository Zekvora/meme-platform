"""
MemePlatform - Unified Runner
Запускает Telegram бота и веб-сервер одной командой
"""
import asyncio
import logging
import threading
import uvicorn

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import MenuButtonWebApp, WebAppInfo

from config import BOT_TOKEN, LOG_LEVEL, WEB_URL
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

# Web server config
WEB_HOST = "0.0.0.0"
WEB_PORT = 8000


def run_web_server():
    """Run FastAPI web server in a separate thread."""
    config = uvicorn.Config(
        "web_app:app",
        host=WEB_HOST,
        port=WEB_PORT,
        log_level="info",
        reload=False
    )
    server = uvicorn.Server(config)
    server.run()


async def main():
    """Main function - starts bot and web server."""
    logger.info("=" * 50)
    logger.info("🚀 Starting MemePlatform...")
    logger.info("=" * 50)
    
    # Initialize databases
    await init_db()
    await db_new.init_db()
    logger.info("✅ Databases initialized")
    
    # Start web server in background thread
    web_thread = threading.Thread(target=run_web_server, daemon=True)
    web_thread.start()
    logger.info(f"✅ Web server started at http://localhost:{WEB_PORT}")
    
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
    dp.include_router(admin_router)
    dp.include_router(user_router)
    
    # Set Menu Button (left side of input field)
    try:
        await bot.set_chat_menu_button(
            menu_button=MenuButtonWebApp(
                text="🎭 Каталог",
                web_app=WebAppInfo(url=f"{WEB_URL}/miniapp")
            )
        )
        logger.info("✅ Menu button set")
    except Exception as e:
        logger.warning(f"Could not set menu button: {e}")
    
    logger.info("✅ Telegram bot is ready!")
    logger.info("=" * 50)
    logger.info("📱 Open Telegram and send /start to the bot")
    logger.info(f"🌐 Web interface: http://localhost:{WEB_PORT}")
    logger.info("=" * 50)
    
    # Start polling
    await dp.start_polling(bot, allowed_updates=["message", "callback_query"])


if __name__ == "__main__":
    asyncio.run(main())
