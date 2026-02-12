from datetime import datetime
from typing import Callable, Awaitable, Dict, Any

from aiogram import BaseMiddleware
from aiogram.types import CallbackQuery, Message, TelegramObject
from loguru import logger

from bot.db.db import async_session
from bot.services.user_service import UserService
from bot.i18n.locale import detect_locale


class LocaleMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        message = data.get("message")
        callback = data.get("callback_query")

        if message is None and isinstance(event, Message):
            message = event
        if callback is None and isinstance(event, CallbackQuery):
            callback = event

        telegram_user = None

        if message:
            telegram_user = message.from_user
        elif callback:
            telegram_user = callback.from_user

        if not telegram_user:
            return await handler(event, data)

        async with async_session() as session:
            user_service = UserService(session)
            user = await user_service.get_by_telegram_id(telegram_user.id)

            if user:
                user.last_active_at = datetime.utcnow()
                await session.commit()

                locale = user.language
                logger.debug(f"Locale from DB: {locale}")
            else:
                locale = detect_locale(message or callback)
                logger.debug(f"Locale from Telegram: {locale}")

            data["locale"] = locale
            data["user"] = user
            data["user_service"] = user_service
            data["db_session"] = session

            return await handler(event, data)