# bot/setup.py

from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties

from bot.config.settings import settings  # pydantic-settings
from bot.middlewares.locale import LocaleMiddleware
from bot.handlers import register_handlers


def setup_bot() -> tuple[Bot, Dispatcher]:
    """
    Composition root.
    Creates and configures all application dependencies.
    """

    # === Bot ===
    bot = Bot(
        token=settings.BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )

    # === Dispatcher ===
    dp = Dispatcher()

    # === Middlewares ===
    dp.message.middleware(LocaleMiddleware())
    dp.callback_query.middleware(LocaleMiddleware())

    # === Register handlers ===
    register_handlers(dp)

    return bot, dp