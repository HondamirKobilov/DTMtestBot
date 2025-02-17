from typing import Union
from aiogram import types
from aiogram.dispatcher import FSMContext
from data.texts import const_text
from filters import F
from keyboards.inline.inline_admin import admin_main_menu
from loader import dp

@dp.message_handler(F.AdminFilter(), commands="admin", state='*', run_task=True)
@dp.callback_query_handler(F.AdminFilter(), lambda c: c.data == "admin_back", state="*")
async def admin_start(message: Union[types.Message, types.CallbackQuery], state: FSMContext):
    fullname = message.from_user.full_name
    admin_text = const_text("admin_start").format(fullname=fullname)
    if isinstance(message, types.CallbackQuery):
        await message.message.edit_text(admin_text, reply_markup=admin_main_menu)
    else:
        await message.answer(admin_text, reply_markup=admin_main_menu)
    await state.finish()
