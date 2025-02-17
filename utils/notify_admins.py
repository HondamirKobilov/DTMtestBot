import logging

from aiogram import Dispatcher

from data.config import ADMINS
from keyboards.default.default_user import kb_main_menu


async def on_startup_notify(dp: Dispatcher):
    for admin in ADMINS:
        try:
            await dp.bot.send_message(admin, "Bot ishga tushdi", reply_markup=kb_main_menu('uz'))
        except Exception as err:
            logging.exception(err)
