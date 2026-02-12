from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from loguru import logger

from bot.i18n.loader import get_text as _
from bot.keyboards.language import get_language_keyboard
from bot.db.models.user import User

router = Router()


@router.message(Command("start"))
async def start_handler(
    message: Message,
    locale: str,
    user: User | None,
):
    telegram_id = message.from_user.id

    logger.info(f"/start | tg_id={telegram_id}")

    if user:
        logger.info(f"User exists | tg_id={telegram_id}")
        await message.answer(
            _("hello_again_message", locale=locale)
        )
        return

    logger.info(f"User not registered | tg_id={telegram_id}")

    await message.answer(
        _("choose_language_message", locale=locale),
        reply_markup=get_language_keyboard(),
    )