from aiogram import Router, types
from aiogram.types import InlineQueryResultPhoto, InlineQueryResultArticle, InputTextMessageContent

from DB.vk_photo import WallPost, PhotoPost
from filters.format_string import transform_string
from handlers.vk_parse import vk_get_wall_post
from lexicon.lexicon import LEXICON_RU
import hashlib
from handlers import vk_parse
from config_data.config import bot
from DB import vk_photo, usersDB

router = Router()


@router.inline_query()
async def inline_get_photo(query: types.InlineQuery):
    text = query.query
    result_id: str = hashlib.md5(text.encode()).hexdigest()
    if '=wall' in text and '=photo' not in text:
        wall_post: WallPost = vk_get_wall_post(text)
        if wall_post is None:
            return
        usersDB.add_user_query(query.from_user.id, query.from_user.username, query.query)
        user = usersDB.get_user(query.from_user.id, query.from_user.username)
        if len(wall_post.photos) == 0:
            photos = [InlineQueryResultArticle(id=result_id, description=transform_string(wall_post.caption,
                                                                                          user.public_preview,
                                                                                          wall_post.public_name,
                                                                                          wall_post.photo_info.owner_id,
                                                                                          wall_post.wall_post_link),
                                               title=wall_post.public_name,
                                               thumbnail_url=wall_post.public_photo,
                                               input_message_content=InputTextMessageContent(message_text=wall_post.caption,
                                                                                             parse_mode='HTML'))]
            await query.answer(photos, cache_time=1, is_personal=False)
        else:
            if wall_post.photo_info and not vk_photo.check_photo(wall_post.photo_info):
                mes = await bot.send_photo(chat_id=972753303, photo=wall_post.photos[0], disable_notification=True)
                await mes.delete()
            photos = [InlineQueryResultPhoto(id=result_id, thumbnail_url=wall_post.photos[0], photo_url=wall_post.photos[0],
                                             caption=transform_string(wall_post.caption,
                                                                      user.public_preview,
                                                                      wall_post.public_name,
                                                                      wall_post.photo_info.owner_id,
                                                                      wall_post.wall_post_link))]

            await query.answer(photos, cache_time=1, is_personal=False)
    else:
        photo_obj = vk_parse.vk_get_photo(text)
        if photo_obj:
            usersDB.add_user_query(query.from_user.id, query.from_user.username, query.query)
            if not vk_photo.check_photo(photo_obj.photo_info):
                mes = await bot.send_photo(chat_id=972753303, photo=photo_obj.photo, disable_notification=True)
                await mes.delete()

        photo = photo_obj or PhotoPost(thumbnail=LEXICON_RU['thumbnail_inline_photo'],
                                       photo=LEXICON_RU['default_inline_photo'],
                                       photo_info=None)

        photos = [InlineQueryResultPhoto(id=result_id,
                                         thumbnail_url=photo.thumbnail,
                                         photo_url=photo.photo)]

        await query.answer(photos, cache_time=1, is_personal=False)
