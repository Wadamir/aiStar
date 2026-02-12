from aiogram import Router, F
from aiogram.types import CallbackQuery
from loguru import logger

from bot.i18n.loader import get_text as _
from bot.services.user_service import UserService

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