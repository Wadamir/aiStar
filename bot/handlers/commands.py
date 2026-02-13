from pathlib import Path

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from loguru import logger

from bot.i18n.loader import get_text as _
from bot.keyboards.language import get_language_keyboard

from bot.services.song_service import SongService
from bot.keyboards.style import get_style_keyboard

from bot.db.models.user import User

from bot.config.settings import settings

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



@router.message(Command("debug"))
async def debug_handler(
    message: Message,
    locale: str,
    user: User | None,
    db_session,
):
    if not user:
        await message.answer(
            _("please_register", locale=locale)
        )
        return

    if message.from_user.id not in settings.ADMIN_IDS:
        await message.answer("Access denied")
        return

    test_file = Path("storage/test.ogg")

    if not test_file.exists():
        await message.answer("Test file not found")
        return

    song_service = SongService(db_session)

    # Create song record manually
    song = await song_service.create_song(
        user_id=user.id,
        original_file=str(test_file),
    )

    await message.answer(
        _("choose_style", locale=locale),
        reply_markup=get_style_keyboard(song.id),
    )