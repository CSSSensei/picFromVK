from aiogram import Router
from aiogram.types import Message
from filters import filters

router = Router()

router.message.filter(filters.AdminUser())


# TODO поменять эту хуету

@router.message()
async def send_echo(message: Message):
    await message.answer(message.text)
