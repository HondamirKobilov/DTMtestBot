from datetime import datetime

from aiogram import types
from aiogram.dispatcher import FSMContext

from data.texts import const_text
from filters import F
from keyboards.inline.inline_admin import admin_back_menu
from loader import dp
from utils.database.functions import f_user


@dp.callback_query_handler(F.AdminFilter(), text="admin_statistics", state="*", run_task=True)
async def handler_users(call: types.CallbackQuery, state: FSMContext):
    try:
        all_users = await f_user.count_users()
        active_users = await f_user.count_active_users()
        today_users = await f_user.get_daily_users_count(datetime.today().strftime('%Y-%m-%d'))
        premium_users = await f_user.get_premium_users_count()
        statistics_text = const_text("admin_statistics").format(
            all_users=all_users,
            active_users=active_users,
            today_users=today_users,
            premium_users=premium_users
        )
        await call.message.edit_text(statistics_text, reply_markup=admin_back_menu)
    except Exception as exception:
        print("statistics error: " + str(exception))
