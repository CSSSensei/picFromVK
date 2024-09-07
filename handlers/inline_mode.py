from aiogram import Router, types
from aiogram.types import InlineQueryResultPhoto
from lexicon.lexicon import LEXICON_RU
import hashlib
from handlers import vk_parse
from config_data.config import bot
from DB import vk_photo

router = Router()


@router.inline_query()
async def inline_get_photo(query: types.InlineQuery):
    text = query.query
    photo_id = vk_parse.vk_get_photo(text)
    result_id: str = hashlib.md5(text.encode()).hexdigest()
    if photo_id and not vk_photo.check_photo(photo_id[2]):
        mes = await bot.send_photo(chat_id=972753303, photo=photo_id[1], disable_notification=True)
        await mes.delete()
    photo = photo_id if photo_id else [LEXICON_RU['thumbnail_inline_photo'], LEXICON_RU['default_inline_photo']]

    photos = [InlineQueryResultPhoto(id=result_id, thumbnail_url=photo[0], photo_url=photo[1])]

    await query.answer(photos, cache_time=1, is_personal=False)
