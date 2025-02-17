# from aiogram import types
# from aiogram.dispatcher import FSMContext
#
# from data.texts import text
# from handlers.users.main.start import user_start_handler
# from keyboards.default.default_user import *
# from loader import dp
# from utils.database.functions import f_user
# from utils.database.models import User
#
#
# @dp.message_handler(state="*")
# async def echo_handler(message: types.Message, state: FSMContext):
#     user_id = message.from_user.id
#     user: User = await f_user.select_user(user_id)
#     await user_start_handler(message, state)
#
#
# @dp.callback_query_handler(state="*")
# async def any_callback_query_handler(call: types.CallbackQuery, state: FSMContext):
#     print(call.data)
#     print("000000")
#     user_id = call.from_user.id
#     language = await f_user.select_user_language(user_id)
#     try:
#         await call.message.delete()
#     except:
#         pass
#     await state.finish()
#     await call.message.answer(text("user_start", language), reply_markup=kb_main_menu(language))
