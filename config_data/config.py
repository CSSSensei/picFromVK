from dotenv import load_dotenv, find_dotenv
from dataclasses import dataclass
import os
from aiogram import Bot

load_dotenv(find_dotenv())


@dataclass
class TgBot:
    token: str = os.getenv('BOT_TOKEN')
    MAX_SYMBOLS: int = 800
    settings_name = 'Настройки'


@dataclass
class VkParse:
    token: str = os.getenv('VKTOKEN')
    version: int = 5.92


@dataclass
class MusicParse:
    token: str = os.getenv('YANDEX_TOKEN')
    song_id_pattern: str = r'https://music\.yandex\.ru/album/(\d+)/track/(\d+)'
    temp_path: str = 'temp'


@dataclass
class Config:
    tg_bot: TgBot
    vk_parse: VkParse
    music_parse: MusicParse


def load_config() -> Config:
    return Config(tg_bot=TgBot(), vk_parse=VkParse(), music_parse=MusicParse())


config: Config = load_config()

bot = Bot(token=config.tg_bot.token, parse_mode="HTML")
