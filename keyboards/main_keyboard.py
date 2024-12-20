import datetime
from typing import Union

from aiogram.types import InlineKeyboardButton, KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardMarkup

from DB import usersDB
from DB.usersDB import get_len_music_queries
from config_data.config import config, bot
from filters import format_string
from handlers.callback import CutMessageCallBack, SetsCallBack
from handlers import callback

settings_button: KeyboardButton = KeyboardButton(
    text=config.tg_bot.settings_name)
basic_keyboard: ReplyKeyboardMarkup = ReplyKeyboardMarkup(
    keyboard=[[settings_button]], resize_keyboard=True, one_time_keyboard=False)


async def get_users_by_page(user_id: int, page: int = 1, message_id: Union[int, None] = None):
    users = usersDB.get_users_from_db()
    txt = f'Всего пользователей: <b>{len(users)}</b>\n\n'
    for user in users:
        memes_amount = len((usersDB.get_user_queries(user.user_id)).queries)
        emoji = '😐'
        if memes_amount > 10:
            emoji = '🤣'
        elif memes_amount > 0:
            emoji = '😂'
        line = (f'<b>{"@" + user.username if user.username else "🐸"}</b> | <i>{user.user_id}</i> |' +
                (' 👑 |' if user.admin else '') + f' {emoji} {memes_amount}') + f' | 🎧 {get_len_music_queries(user.user_id)}\n'
        txt += line
    txt = format_string.split_text(txt, config.tg_bot.MAX_SYMBOLS)
    if not message_id:
        await bot.send_message(chat_id=user_id, text=txt[page - 1], reply_markup=page_keyboard(action=1, page=page, max_page=len(txt)))
    else:
        await bot.edit_message_text(chat_id=user_id, message_id=message_id, text=txt[page - 1],
                                    reply_markup=page_keyboard(action=1, page=page, max_page=len(txt)))


async def user_query_by_page(user_id: int, user_id_to_find: Union[int, None], page: int = 1, message_id: Union[int, None] = None):
    query = (usersDB.get_user_queries(user_id_to_find)).queries
    if not user_id_to_find or not query:
        await bot.send_message(chat_id=user_id, text='Неправильный <i>user_id</i> или этот пользователь не отправлял запросы')
        return
    username = usersDB.get_user(user_id_to_find).username
    txt = f'История запросов <b>{"@" + username if username else user_id_to_find}</b>\n\n'
    for unix_time, text in query.items():
        query_time = datetime.datetime.utcfromtimestamp(unix_time) + datetime.timedelta(hours=3)
        user_query = format_string.format_string(text).replace("\n", "\t")
        line = f'[{query_time}]: <blockquote>{user_query}</blockquote>\n\n'
        if len(line) + len(txt) < 4096:
            txt += line
    txt = format_string.split_text(txt, config.tg_bot.MAX_SYMBOLS)
    if not message_id:
        await bot.send_message(chat_id=user_id, text=txt[page - 1].replace('\t', '\n'),
                               reply_markup=page_keyboard(action=2, page=page, max_page=len(txt), user_id=user_id_to_find))
    else:
        await bot.edit_message_text(chat_id=user_id, message_id=message_id, text=txt[page - 1].replace('\t', '\n'),
                                    reply_markup=page_keyboard(action=2, page=page, max_page=len(txt), user_id=user_id_to_find))


def page_keyboard(action: int, page: int, max_page: int, user_id: int = 0):
    array_buttons: list[list[InlineKeyboardButton]] = [[]]
    if page > 1:
        array_buttons[0].append(
            InlineKeyboardButton(text='<', callback_data=CutMessageCallBack(action=action, page=page - 1, user_id=user_id).pack())
        )
    array_buttons[0].append(
        InlineKeyboardButton(text=str(page), callback_data=CutMessageCallBack(action=-1).pack())
    )
    if page < max_page:
        array_buttons[0].append(
            InlineKeyboardButton(text='>', callback_data=CutMessageCallBack(action=action, page=page + 1, user_id=user_id).pack())
        )
    if len(array_buttons[0]) == 1:
        return None
    markup = InlineKeyboardMarkup(inline_keyboard=array_buttons)
    return markup


def get_keyboard(show_name: bool = True):
    array_buttons: list[list[InlineKeyboardButton]] = []
    if not show_name:
        txt = 'Указывать автора'
        action = callback.SETShowPublicName
    else:
        txt = 'Отключить имя автора'
        action = callback.SETDONOTShowPublicName
    array_buttons.append([InlineKeyboardButton(text=txt, callback_data=SetsCallBack(action=action).pack())])
    markup = InlineKeyboardMarkup(inline_keyboard=array_buttons)
    return markup


async def user_music_query_by_page(user_id: int, user_id_to_find: Union[int, None], page: int = 1, message_id: Union[int, None] = None):
    query_list = usersDB.get_music_queries_by_user(user_id_to_find)
    if not user_id_to_find or not query_list:
        await bot.send_message(chat_id=user_id, text='Неправильный <i>user_id</i> или этот пользователь не отправлял запросы')
        return
    username = usersDB.get_user(user_id_to_find).username
    txt = f'История запросов <b>{"@" + username if username else user_id_to_find}</b>\n\n'
    query: usersDB.MusicQuery
    for query in query_list:
        query_time = datetime.datetime.utcfromtimestamp(query.time) + datetime.timedelta(hours=3)
        user_query = f'<b>{query.song.artists}</b> — {query.song.title}'
        line = f'[{query_time}]: <blockquote>{user_query}</blockquote>\n\n'
        if len(line) + len(txt) < 4096:
            txt += line
    txt = format_string.split_text(txt, config.tg_bot.MAX_SYMBOLS)
    if not message_id:
        await bot.send_message(chat_id=user_id, text=txt[page - 1].replace('\t', '\n'),
                               reply_markup=page_keyboard(action=3, page=page, max_page=len(txt), user_id=user_id_to_find))
    else:
        await bot.edit_message_text(chat_id=user_id, message_id=message_id, text=txt[page - 1].replace('\t', '\n'),
                                    reply_markup=page_keyboard(action=3, page=page, max_page=len(txt), user_id=user_id_to_find))
