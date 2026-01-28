"""
MemeMakerBot - Middlewares (Rate Limiting, Logging, etc.)
"""
import logging
from typing import Callable, Any, Awaitable
from datetime import datetime
from cachetools import TTLCache

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Message, CallbackQuery

from config import RATE_LIMIT_MESSAGES, RATE_LIMIT_PERIOD, ADMIN_IDS
from database import log_event, get_or_create_user
from locales import get_text, detect_language

logger = logging.getLogger(__name__)


class RateLimitMiddleware(BaseMiddleware):
    """Rate limiting middleware to prevent spam."""
    
    def __init__(self):
        self.cache = TTLCache(maxsize=10000, ttl=RATE_LIMIT_PERIOD)
    
    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        user_id = None
        
        if isinstance(event, Message) and event.from_user:
            user_id = event.from_user.id
        elif isinstance(event, CallbackQuery) and event.from_user:
            user_id = event.from_user.id
        
        if user_id:
            # Admins bypass rate limit
            if user_id in ADMIN_IDS:
                return await handler(event, data)
            
            # Check rate limit
            key = f"rate:{user_id}"
            count = self.cache.get(key, 0)
            
            if count >= RATE_LIMIT_MESSAGES:
                logger.warning(f"Rate limit exceeded for user {user_id}")
                if isinstance(event, Message):
                    lang = detect_language(event.from_user.language_code)
                    await event.answer(get_text("error_rate_limit", lang))
                elif isinstance(event, CallbackQuery):
                    lang = detect_language(event.from_user.language_code)
                    await event.answer(get_text("error_rate_limit", lang), show_alert=True)
                return
            
            self.cache[key] = count + 1
        
        return await handler(event, data)


class UserTrackingMiddleware(BaseMiddleware):
    """Track users and their language preferences."""
    
    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        user = None
        
        if isinstance(event, Message) and event.from_user:
            user = event.from_user
        elif isinstance(event, CallbackQuery) and event.from_user:
            user = event.from_user
        
        if user:
            lang = detect_language(user.language_code)
            await get_or_create_user(
                user_id=user.id,
                username=user.username,
                first_name=user.first_name,
                language=lang
            )
            data["user_lang"] = lang
        
        return await handler(event, data)


class ErrorLoggingMiddleware(BaseMiddleware):
    """Log errors to database."""
    
    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        try:
            return await handler(event, data)
        except Exception as e:
            user_id = None
            if isinstance(event, (Message, CallbackQuery)) and event.from_user:
                user_id = event.from_user.id
            
            logger.exception(f"Error processing update: {e}")
            await log_event("error", user_id, str(e)[:500])
            
            # Send generic error message
            try:
                lang = data.get("user_lang", "ru")
                if isinstance(event, Message):
                    await event.answer(get_text("error_generic", lang))
                elif isinstance(event, CallbackQuery):
                    await event.answer(get_text("error_generic", lang), show_alert=True)
            except Exception:
                pass
            
            raise
