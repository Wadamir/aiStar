from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

STYLES = {
    "rap": "🎤 Rap",
    "pop": "🎵 Pop",
    "rock": "🎸 Rock",
}


def get_style_keyboard(song_id: int) -> InlineKeyboardMarkup:
    buttons = []

    for style_code, label in STYLES.items():
        buttons.append(
            InlineKeyboardButton(
                text=label,
                callback_data=f"style:{song_id}:{style_code}",
            )
        )

    return InlineKeyboardMarkup(
        inline_keyboard=[[btn] for btn in buttons]
    )