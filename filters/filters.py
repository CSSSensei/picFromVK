from aiogram.filters import BaseFilter
from aiogram.types import Message


class AdminUser(BaseFilter):
    async def __call__(self, message: Message) -> bool:
        # TODO поменять эту хуету
        return True

