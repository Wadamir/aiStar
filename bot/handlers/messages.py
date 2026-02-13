from aiogram import Router, F
from aiogram.types import Message
from loguru import logger

from bot.config.settings import settings
from bot.i18n.loader import get_text as _
from bot.services.song_service import SongService
from bot.services.storage_service import StorageService
from bot.db.models.user import User
from bot.keyboards.style import get_style_keyboard

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

    # Determine daily limit (admin override)
    if user.telegram_id in settings.ADMIN_IDS:
        daily_limit = 100
    else:
        daily_limit = user.plan.daily_limit

    if user.songs_count >= daily_limit:
        await message.answer(
            _("daily_limit_reached", locale=locale)
        )
        return

    file = await message.bot.get_file(message.voice.file_id)
    file_path = file.file_path

    storage_service = StorageService()
    local_filename = storage_service.build_voice_path(
        message.voice.file_id
    )

    await message.bot.download_file(
        file_path,
        destination=local_filename,
    )

    logger.info(
        f"Voice saved | tg_id={user.telegram_id} | file={local_filename}"
    )

    song_service = SongService(db_session)

    song = await song_service.create_song(
        user_id=user.id,
        original_file=str(local_filename),
    )

    user.songs_count += 1
    await db_session.commit()

    await message.answer(
        _("choose_style", locale=locale),
        reply_markup=get_style_keyboard(song.id),
    )