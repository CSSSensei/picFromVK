from dotenv import load_dotenv, find_dotenv
from dataclasses import dataclass
import os
from aiogram import Bot

load_dotenv(find_dotenv())


@dataclass
class TgBot:
    token: str = os.getenv('BOT_TOKEN')


@dataclass
class VkParse:
    token: str = os.getenv('VKTOKEN')
    version: int = 5.92


@dataclass
class Config:
    tg_bot: TgBot
    vk_parse: VkParse


def load_config(path: str | None = None) -> Config:
    return Config(tg_bot=TgBot(), vk_parse=VkParse())


config: Config = load_config()

bot = Bot(token=config.tg_bot.token, parse_mode="HTML")
