from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardMarkup

STYLES = {
    "rap": "🎤 Rap",
    "pop": "🎵 Pop",
    "rock": "🎸 Rock",
    "vocal": "🎙️ Vocal",
}


def get_style_keyboard(song_id: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    for style_code, style_name in STYLES.items():
        builder.button(
            text=style_name,
            callback_data=f"style:{song_id}:{style_code}"
        )

    builder.adjust(2)  # 2 buttons per row

    return builder.as_markup()