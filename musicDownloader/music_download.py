import asyncio
import aiohttp
import aiofiles

import os

from re import search
from datetime import datetime
from typing import List, Tuple, Union, Optional

from yandex_music import ClientAsync, Artist, Album, Track
from yandex_music.exceptions import BadRequestError

from mutagen.mp3 import MP3
from mutagen.id3 import (ID3, TIT2, TPE1, TPE2, TALB, TYER, TDRL, APIC)
from config_data.config import config

YANDEX_TOKEN = config.music_parse.token
YANDEX_SONG_ID_PATTERN = config.music_parse.song_id_pattern
TEMP_PATH = config.music_parse.temp_path

__client = ClientAsync(YANDEX_TOKEN)


def __format_date(date_str: str):
    if not date_str:
        return ''
    date = datetime.fromisoformat(date_str)
    return date


def __make_feats_artists_title(artists: List[Artist]):
    return 'feat.' + ', '.join([artist.name for artist in artists[1:]])


async def __download_img(album_id: str, song_id: str, img_link: str) -> str:
    save_path = f'{TEMP_PATH}/{album_id}{song_id}.png'

    async with aiohttp.ClientSession() as session:
        async with session.get('https://' + img_link.replace('%%', '1000x1000')) as response:
            if response.status == 200:
                async with aiofiles.open(save_path, 'wb') as img:
                    async for data in response.content.iter_any():
                        await img.write(data)
                return save_path
    return ""


async def __decoration_song(album: Album, song: Track, song_path: str):
    audio = MP3(song_path, ID3=ID3)

    if audio.tags is None:
        audio.add_tags()

    feats = __make_feats_artists_title(song.artists)
    date = __format_date(album.release_date)
    img = await __download_img(str(album.id), str(song.id), album.cover_uri)

    # - TIT2 - Название трека (Title)
    # - TPE1 - Исполнитель (Artist)
    # - TALB - Альбом (Album)
    # - TYER - Год (Year)
    # - TPE2 - Исполнитель альбома (Album Artist)
    # - TDRL - Дата релиза (Release Time)
    # - APIC - Вложенные изображения (Attached Picture)

    audio.tags.add(TIT2(encoding=3, text=song.title))
    audio.tags.add(TALB(encoding=3, text=album.title))

    audio.tags.add(TPE1(encoding=3, text=song.artists[0].name))

    if feats != 'feat.':
        audio.tags.add(TPE2(encoding=3, text=feats))

    if date != '':
        audio.tags.add(TYER(encoding=3, text=str(date.year)))
        audio.tags.add(TDRL(encoding=3, text=date.strftime("%Y-%m-%d")))

    if img:
        with open(img, 'rb') as img_file:
            img_data = img_file.read()

        audio.tags.add(APIC(mime='image/png', type=3, desc='Cover', data=img_data))
        os.remove(img)
    audio.save()


async def __download_song(album_id: str, song_id: str) -> Optional[Tuple[str, str, str]]:
    try:
        album = (await __client.albums(album_id))[0]
        song = (await __client.tracks(song_id))[0]

        save_path = f'{TEMP_PATH}/{album_id}{song_id}.mp3'
        await song.download_async(save_path)

    except BadRequestError:
        return None

    await __decoration_song(album, song, save_path)
    return save_path, song.title, ", ".join([a.name for a in song.artists])


async def download_song(link) -> Optional[Tuple[str, str, str]]:
    song = search(YANDEX_SONG_ID_PATTERN, link)

    if song:
        song_id = song.group(2)
        album_id = song.group(1)
        song_info = await __download_song(album_id=album_id, song_id=song_id)
        return song_info
    return None

if __name__ == '__main__':
    asyncio.run(download_song('https://music.yandex.ru/album/10946852/track/66897041?utm_source=desktop&utm_medium=copy_link'))
