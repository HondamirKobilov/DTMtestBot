from typing import Union

from aiogram import types
from aiogram.dispatcher.filters import BoundFilter
from aiogram.types import Message, CallbackQuery

from data.config import ADMINS


class ViaFilter(BoundFilter):
    async def check(self, message: types.Message) -> bool:
        return message.via_bot is not None


class AdminFilter(BoundFilter):
    key = 'admin'

    async def check(self, data: Union[Message, CallbackQuery]) -> bool:
        return str(data.from_user.id) in ADMINS


class MyFilter(BoundFilter):
    key = 'my'

    async def check(self, data: Union[Message, CallbackQuery]) -> bool:
        return str(data.from_user.id) == ADMINS[0]


class CallBackFilter(BoundFilter):
    key = 'callback'

    def __init__(self, kw: str) -> None:
        super().__init__()
        self.kw = kw

    async def check(self, call: CallbackQuery) -> bool:
        return self.kw in call.data
