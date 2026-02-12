from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from bot.i18n.languages import get_active_languages


def get_language_keyboard() -> InlineKeyboardMarkup:
    buttons = []

    for code, meta in get_active_languages().items():
        buttons.append(
            InlineKeyboardButton(
                text=f"{meta['flag']} {meta['label']}",
                callback_data=f"lang_{code}",
            )
        )

    return InlineKeyboardMarkup(
        inline_keyboard=[buttons]
    )