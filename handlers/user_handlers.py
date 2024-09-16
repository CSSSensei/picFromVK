from typing import Optional

from aiogram import Router, F
import random
from aiogram.filters import Command, CommandStart
from aiogram.types import Message, InputMediaPhoto

from DB.vk_photo import WallPost
from DB import usersDB
from filters.format_string import transform_string
from handlers import vk_parse
from handlers.vk_parse import vk_get_wall_post, config
from lexicon.lexicon import LEXICON_RU
from keyboards import main_keyboard

router = Router()


@router.message(CommandStart())  # /start
async def cmd_start(message: Message):
    await message.answer(text=LEXICON_RU['/start'], reply_markup=main_keyboard.basic_keyboard)
    usersDB.add_user(message.from_user.id, message.from_user.username)


@router.message(Command(commands='help'))  # /help
async def cmd_help(message: Message):
    await message.answer(text=LEXICON_RU['/help'], disable_web_page_preview=True, reply_markup=main_keyboard.basic_keyboard)


@router.message(Command(commands='about'))  # /help
async def cmd_about(message: Message):
    await message.answer(text=LEXICON_RU['/about'], reply_markup=main_keyboard.basic_keyboard)


@router.message(Command(commands='test'))  # /test
async def cmd_test(message: Message):
    await message.answer(text='&laquo;{lines}&raquo;', parse_mode='HTML')


@router.message(F.text == LEXICON_RU['_password'])
async def get_verified(message: Message):
    usersDB.set_admin(message.from_user.id)
    await message.answer('Теперь ты админ')


@router.message(F.text == config.tg_bot.settings_name)
async def settings_message(message: Message, edit: Optional[bool] = False, user_id: Optional[int] = None):
    user = usersDB.get_user(user_id if user_id else message.from_user.id)
    txt = ('<b>Твои текущие настройки</b>\n\n'
           f'{"Показывать название паблика" if user.public_preview else "<u>НЕ</u> показывать название паблика"}')
    if edit:
        await message.edit_text(txt, reply_markup=main_keyboard.get_keyboard(user.public_preview))
    else:
        await message.answer(txt, reply_markup=main_keyboard.get_keyboard(user.public_preview))


@router.message()
async def user_send_photo(message: Message):
    if message.text:
        if 'wall' in message.text and 'photo' not in message.text:
            wall_post: WallPost = vk_get_wall_post(message.text)
            if wall_post is None:
                await message.answer(LEXICON_RU['no_photo'], reply_markup=main_keyboard.basic_keyboard)
                return
            user = usersDB.get_user(message.from_user.id)
            if len(wall_post.photos) == 0:
                await message.answer(transform_string(wall_post.caption,
                                                      user.public_preview,
                                                      wall_post.public_name,
                                                      wall_post.photo_info.owner_id,
                                                      wall_post.wall_post_link),
                                     reply_markup=main_keyboard.basic_keyboard)
            else:
                media = [
                    InputMediaPhoto(media=photo, caption=transform_string(wall_post.caption,
                                                                          user.public_preview,
                                                                          wall_post.public_name,
                                                                          wall_post.photo_info.owner_id,
                                                                          wall_post.wall_post_link))
                    if i == 0 else InputMediaPhoto(media=photo) for i, photo in enumerate(wall_post.photos)
                ]
                await message.answer_media_group(media=media, reply_markup=main_keyboard.basic_keyboard)
            usersDB.add_user_query(message.from_user.id, message.from_user.username, message.text)
        else:
            photo = vk_parse.vk_get_photo(message.text)
            if photo:
                await message.answer_photo(photo=photo.photo)
                usersDB.add_user_query(message.from_user.id, message.from_user.username, message.text)
            else:
                await message.answer(LEXICON_RU['no_photo'], reply_markup=main_keyboard.basic_keyboard)
    else:
        await message.answer(random.choice(LEXICON_RU['hz_answers']), reply_markup=main_keyboard.basic_keyboard)
