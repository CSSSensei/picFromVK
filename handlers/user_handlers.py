from aiogram import Router
import random
from aiogram.filters import Command, CommandStart
from aiogram.types import Message
from handlers import vk_parse
from lexicon.lexicon import LEXICON_RU

router = Router()


@router.message(CommandStart())  # /start
async def cmd_start(message: Message):
    await message.answer(text=LEXICON_RU['/start'])


@router.message(Command(commands='help'))  # /help
async def cmd_help(message: Message):
    await message.answer(text=LEXICON_RU['/help'])


@router.message()
async def user_send_photo(message: Message):
    if message.text:
        photo = vk_parse.vk_get_photo(message.text)
        if photo:
            await message.answer_photo(photo=photo[1])
        else:
            await message.answer(LEXICON_RU['no_photo'])
    else:
        await message.answer(random.choice(LEXICON_RU['hz_answers']))
