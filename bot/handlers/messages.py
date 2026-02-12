from aiogram import Router, F
from aiogram.types import Message

router = Router()


@router.message(F.voice)
async def voice_handler(message: Message):
    await message.answer("STYLE_SELECTION_MESSAGE")