from typing import Union
from aiogram import types, Dispatcher
from aiogram.dispatcher.handler import CancelHandler, current_handler
from aiogram.dispatcher.middlewares import BaseMiddleware
from aiogram.utils.exceptions import Throttled

async def message_throttled(message: Union[types.Message, types.CallbackQuery, types.InlineQuery], throttled: Throttled):
    try:
        if isinstance(message, types.InlineQuery):
            if throttled.exceeded_count <= 2:
                return
        if throttled.exceeded_count <= 2:
            await message.answer("Iltimos kuting...")
        else:
            if isinstance(message, types.CallbackQuery):
                await message.answer()
    except: pass

class ThrottlingMiddleware(BaseMiddleware):
    def __init__(self, limit=0.8, key_prefix='antiflood_'):
        self.rate_limit = limit
        self.prefix = key_prefix
        super(ThrottlingMiddleware, self).__init__()

    async def on_process_message(self, message: types.Message, data: dict):
        await self._throttle(message.from_user.id, message)

    async def on_process_callback_query(self, callback_query: types.CallbackQuery, data: dict):
        # await callback_query.answer(callback_query.data)
        await self._throttle(callback_query.from_user.id, callback_query)

    async def on_process_inline_query(self, inline_query: types.InlineQuery, data: dict):
        await self._throttle(inline_query.from_user.id, inline_query)


    async def _throttle(self, user_id, target):
        handler = current_handler.get()
        dispatcher = Dispatcher.get_current()

        if handler:
            limit = getattr(handler, "throttling_rate_limit", self.rate_limit)
            key = getattr(handler, "throttling_key", f"{self.prefix}_{handler.__name__}")
        else:
            limit = self.rate_limit
            key = f"{self.prefix}_message"

        try:
            await dispatcher.throttle(key, rate=limit, user_id=user_id)
        except Throttled as t:
            await message_throttled(target, t)
            raise CancelHandler()
        except Exception as ex:
            print("Throttling error: ", ex)
