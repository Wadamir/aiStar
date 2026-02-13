from aiogram import Router, F
from aiogram.types import Message
from loguru import logger

from bot.i18n.loader import get_text as _
from bot.services.song_service import SongService
from bot.keyboards.style import get_style_keyboard
from bot.db.models.user import User
from bot.exceptions import BotError

router = Router()


@router.message(F.voice)
async def voice_handler(
    message: Message,
    user: User,
    db_session,
    locale: str,
):
    if not user:
        await message.answer(
            _("please_register", locale=locale)
        )
        return

    song_service = SongService(db_session)

    try:
        song = await song_service.handle_voice_upload(
            message=message,
            user=user,
        )

    except BotError as e:
        await message.answer(
            _(getattr(e, "code", "internal_error"), locale=locale)
        )
        return

    logger.info(
        f"Voice accepted | tg_id={user.telegram_id} | song_id={song.id}"
    )

    await message.answer(
        _("choose_style", locale=locale),
        reply_markup=get_style_keyboard(song.id),
    )