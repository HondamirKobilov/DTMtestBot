from aiogram import types
from aiogram.dispatcher import FSMContext

from keyboards.inline.inline_admin import group_empty_buttons, group_exists_buttons
from loader import dp
from states.admin import AdminGroupState
from utils.database.functions.f_group import get_all_groups, create_group


@dp.callback_query_handler(lambda call: call.data == "admin_group", state="*")
async def show_admin_group(call: types.CallbackQuery):
    groups = await get_all_groups()

    if not groups:
        text = "📭 Hali bazaga birorta guruh qo‘shilmagan."
        await call.message.edit_text(text, reply_markup=group_empty_buttons())
    else:
        group = groups[0]
        text = f"✅ Guruh nomi: <b>{group.title}</b>\n@{group.username}\nID: <code>{group.chat_id}</code>"
        await call.message.edit_text(text, reply_markup=group_exists_buttons(), parse_mode="HTML")

    await call.answer()

@dp.callback_query_handler(lambda call: call.data == "admin_add_group")
async def ask_group_chat_id(call: types.CallbackQuery):
    await call.message.edit_text("🆔 Guruhning <b>chat ID</b> ni kiriting:", parse_mode="HTML")
    await AdminGroupState.chat_id.set()
    await call.answer()

@dp.message_handler(state=AdminGroupState.chat_id)
async def ask_group_username(message: types.Message, state: FSMContext):
    await state.update_data(chat_id=int(message.text))
    await message.answer("🔗 Guruhning <b>username</b>ini kiriting (masalan, <code>mygroup</code>):", parse_mode="HTML")
    await AdminGroupState.username.set()

@dp.message_handler(state=AdminGroupState.username)
async def ask_group_title(message: types.Message, state: FSMContext):
    await state.update_data(username=message.text)
    await message.answer("🏷 Guruhning <b>nomi</b>ni kiriting (title):", parse_mode="HTML")
    await AdminGroupState.title.set()

@dp.message_handler(state=AdminGroupState.title)
async def save_group_to_db(message: types.Message, state: FSMContext):
    data = await state.get_data()
    chat_id = data.get("chat_id")
    username = data.get("username")
    title = message.text
    new_group = await create_group(chat_id=chat_id, username=username, title=title)

    if new_group:
        msg = f"✅ Guruh muvaffaqiyatli qo‘shildi:\n\n🏷 <b>{title}</b>\n🔗 @{username}\n🆔 <code>{chat_id}</code>"
        await message.answer(msg, parse_mode="HTML", reply_markup=group_exists_buttons())
    else:
        await message.answer("❌ Guruhni bazaga qo‘shishda xatolik yuz berdi.")

    await state.finish()