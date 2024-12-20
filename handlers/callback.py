from aiogram import Router
from aiogram.filters.callback_data import CallbackData
from aiogram.types import CallbackQuery
from keyboards import main_keyboard
from DB import usersDB
from handlers.user_handlers import settings_message
router = Router()


SETShowPublicName = 0
SETDONOTShowPublicName = 1


class CutMessageCallBack(CallbackData, prefix="cut"):
    action: int
    user_id: int = 0
    page: int = 1


class SetsCallBack(CallbackData, prefix="sets"):
    action: int


@router.callback_query(CutMessageCallBack.filter())
async def cut_message_distributor(callback: CallbackQuery, callback_data: CutMessageCallBack):
    action = callback_data.action
    page = callback_data.page
    user_id = callback_data.user_id
    if action == 1:
        await main_keyboard.get_users_by_page(callback.from_user.id, page, callback.message.message_id)
    elif action == 2:
        await main_keyboard.user_query_by_page(callback.from_user.id, user_id, page, callback.message.message_id)
    elif action == 3:
        await main_keyboard.user_music_query_by_page(callback.from_user.id, user_id, page, callback.message.message_id)
    elif action == -1:
        await callback.answer()


@router.callback_query(SetsCallBack.filter())
async def cut_message_distributor(callback: CallbackQuery, callback_data: SetsCallBack):
    action = callback_data.action
    if action == SETShowPublicName:
        usersDB.set_public_name(callback.from_user.id, True)
    elif action == SETDONOTShowPublicName:
        usersDB.set_public_name(callback.from_user.id, False)
    await settings_message(callback.message, True, callback.from_user.id)
