import asyncio

from aiogram import Bot, Dispatcher
# from config_data.config import Config, load_config
from config_data.config import bot
from handlers import admin_handlers, user_handlers, inline_mode


async def main():
    # config: Config = load_config()
    #
    # bot = Bot(token=config.tg_bot.token)
    dp = Dispatcher()

    dp.include_router(user_handlers.router)
    dp.include_router(admin_handlers.router)
    dp.include_router(inline_mode.router)

    await bot.delete_webhook(drop_pending_updates=True)
    print('Пошла возня')
    await dp.start_polling(bot)


asyncio.run(main())
