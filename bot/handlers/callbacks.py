from pathlib import Path
from aiogram import Router, F
from aiogram.types import CallbackQuery
from loguru import logger

from bot.models.context import JobContext
from bot.workers.queue import JobQueue

from bot.i18n.loader import get_text as _

from bot.services.user_service import UserService
from bot.services.song_service import SongService

router = Router()


@router.callback_query(F.data.startswith("lang_"))
async def language_selected(
    callback: CallbackQuery,
    locale: str,
    user,
    user_service: UserService,
):
    selected_lang = callback.data.split("_")[1]
    telegram_id = callback.from_user.id

    logger.info(
        f"Language selected | tg_id={telegram_id} | lang={selected_lang}"
    )

    if not user:
        user = await user_service.create_user(
            telegram_id=telegram_id,
            username=callback.from_user.username,
            first_name=callback.from_user.first_name,
            last_name=callback.from_user.last_name,
            language=selected_lang,
        )

        logger.success(
            f"User registered | tg_id={telegram_id} | lang={selected_lang}"
        )
    else:
        await user_service.set_language(user, selected_lang)

    await callback.message.edit_reply_markup(reply_markup=None)

    await callback.message.answer(
        _("start_message", locale=selected_lang)
    )

    await callback.answer()


@router.callback_query(F.data.startswith("style:"))
async def style_selected(
    callback: CallbackQuery,
    user,
    db_session,
    job_queue: JobQueue,
    locale: str,
):
    prefix, song_id_str, style_code = callback.data.split(":")
    song_id = int(song_id_str)

    song_service = SongService(db_session)
    song = await song_service.get_song(song_id)

    if not song:
        await callback.answer(
            _("song_not_found", locale=locale),
            show_alert=True,
        )
        return

    if not user or song.user_id != user.id:
        await callback.answer(
            _("not_allowed", locale=locale),
            show_alert=True,
        )
        return

    # Update song with chosen style and mark as queued
    song.style = style_code
    song.status = "queued"
    await db_session.commit()

    logger.info(
        f"Style selected | tg_id={callback.from_user.id} "
        f"| song_id={song_id} | style={style_code}"
    )

    await callback.message.edit_reply_markup(reply_markup=None)

    await callback.message.answer(
        _("processing_started", locale=locale)
    )

    # 🔥 Create job
    ctx = JobContext(
        user_id=user.telegram_id,
        song_id=song.id,
        voice_path=Path(song.original_file),
        chosen_style=style_code,
    )

    # 🔥 Queue
    await job_queue.put(ctx)

    await callback.answer()