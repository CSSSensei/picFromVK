import datetime
from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from DB import usersDB
from filters import filters, format_string
from keyboards import main_keyboard

router = Router()

router.message.filter(filters.AdminUser())


@router.message(Command(commands='get_users'))  # /get_users
async def cmd_get_users(message: Message):
    await main_keyboard.get_users_by_page(message.from_user.id)


@router.message(Command(commands='getcoms'))  # /get_users
async def cmd_getcoms(message: Message):
    await message.answer('/help\n'
                         '/get_users\n'
                         '/query <i>(int)</i> — последние <i>n</i> среди всех запросов\n'
                         '/user_query <i>(user_id)</i> — VK запросы пользователя <i>(user_id)</i>\n'
                         '/user_music_query <i>(user_id)</i> — я.музыка запросы пользователя <i>(user_id)</i>\n'
                         '/about')


@router.message(Command(commands='query'))  # /query
async def cmd_query(message: Message):
    txt = ''
    amount = format_string.find_first_number(message.text)
    if not amount:
        amount = 5
    for user in usersDB.get_last_queries(amount):
        username = usersDB.get_user(user.user_id).username
        line = (f'<i>@{username if username else user.user_id}</i> — '
                f'{", ".join(f"[{datetime.datetime.utcfromtimestamp(unix_time) + datetime.timedelta(hours=3)}]: <blockquote>{format_string.format_string(query)}</blockquote>" for unix_time, query in user.queries.items())}\n\n')
        if len(line) + len(txt) < 4096:
            txt += line
        else:
            try:
                await message.answer(text=txt)
            except Exception as e:
                await message.answer(text=f'Произошла ошибка!\n{e}')
            txt = line
    if len(txt) != 0:
        await message.answer(txt, disable_web_page_preview=True)
    else:
        await message.answer('Запросов не было')


@router.message(Command(commands='user_query'))  # /user_query
async def cmd_user_query(message: Message):
    user_id_to_find = format_string.find_first_number(message.text)
    await main_keyboard.user_query_by_page(message.from_user.id, user_id_to_find)


@router.message(Command(commands='user_music_query'))  # /user_music_query
async def cmd_user_music_query(message: Message):
    user_id_to_find = format_string.find_first_number(message.text)
    await main_keyboard.user_music_query_by_page(message.from_user.id, user_id_to_find)
