from aiogram import types
from aiogram.dispatcher import FSMContext
from keyboards.inline.inline_admin import get_diagnostika_buttons, admin_back_menu, get_diagnostika_detail_buttons, get_confirm_delete_diaginostika_buttons
from loader import dp
from states.admin import AddDiagnostikaState, EditDiagnostikaState
from utils.database.functions.f_diagnostika import create_diagnostika, delete_diagnostika, get_diagnostika_by_id, \
    update_diagnostika

@dp.callback_query_handler(lambda call: call.data == "admin_diaginostika")
async def admin_diagnostika_handler(call: types.CallbackQuery):
    text, keyboard = await get_diagnostika_buttons()
    await call.message.edit_text(text, reply_markup=keyboard)

@dp.callback_query_handler(lambda call: call.data == "admin_add_diagnostika")
async def ask_diagnostika_name(call: types.CallbackQuery):
    await call.message.edit_text("✏️ Iltimos, yangi diagnostika nomini kiriting:", reply_markup=admin_back_menu)
    await AddDiagnostikaState.waiting_for_name.set()

@dp.message_handler(state=AddDiagnostikaState.waiting_for_name)
async def process_diagnostika_name(message: types.Message, state: FSMContext):
    diagnostika_name = message.text.strip()
    await create_diagnostika(diagnostika_name)
    text, keyboard = await get_diagnostika_buttons()
    await message.answer(f"✅ Diagnostika \"{diagnostika_name}\" muvaffaqiyatli qo‘shildi!\n\n{text}",
                         reply_markup=keyboard)
    await state.finish()

@dp.callback_query_handler(lambda call: call.data.startswith("admin_diagnostika:"), state="*")
async def show_diagnostika_details(call: types.CallbackQuery):
    diagnostika_id = int(call.data.replace("admin_diagnostika:", ""))
    text, keyboard = await get_diagnostika_detail_buttons(diagnostika_id)
    await call.message.edit_text(text, reply_markup=keyboard)

@dp.callback_query_handler(lambda call: call.data.startswith("confirm_delete_diagnostika:"))
async def confirm_delete_diagnostika(call: types.CallbackQuery):
    diagnostika_id = int(call.data.replace("confirm_delete_diagnostika:", ""))
    text, keyboard = await get_confirm_delete_diaginostika_buttons(diagnostika_id)
    await call.message.edit_text(text, reply_markup=keyboard)

@dp.callback_query_handler(lambda call: call.data.startswith("delete_diagnostika:"))
async def delete_diagnostika_handler(call: types.CallbackQuery):
    diagnostika_id = int(call.data.replace("delete_diagnostika:", ""))
    diagnostika = await get_diagnostika_by_id(diagnostika_id)
    if not diagnostika:
        await call.answer("❌ Xatolik: Diagnostika topilmadi!", show_alert=True)
        return
    deleted = await delete_diagnostika(diagnostika_id)
    if deleted:
        text, keyboard = await get_diagnostika_buttons()
        await call.message.edit_text(f"✅ \"{diagnostika.name}\" diagnostikasi muvaffaqiyatli o‘chirildi!", reply_markup=keyboard)
    else:
        await call.message.answer("❌ Xatolik: Diagnostikani o‘chirishda muammo yuz berdi!")

@dp.callback_query_handler(lambda call: call.data.startswith("admin_edit_diagnostika:"))
async def ask_for_new_diagnostika_name(call: types.CallbackQuery, state: FSMContext):
    diagnostika_id = int(call.data.replace("admin_edit_diagnostika:", ""))
    diagnostika = await get_diagnostika_by_id(diagnostika_id)

    if not diagnostika:
        await call.answer("❌ Diagnostika topilmadi!", show_alert=True)
        return

    await state.update_data(diagnostika_id=diagnostika_id, old_name=diagnostika.name)
    await call.message.edit_text(
        f"📌 Yangi diagnostika nomini kiriting: (Joriy nom: {diagnostika.name})",
        reply_markup=admin_back_menu
    )
    await EditDiagnostikaState.name.set()

@dp.message_handler(state=EditDiagnostikaState.name)
async def process_new_diagnostika_name(message: types.Message, state: FSMContext):
    new_name = message.text.strip()
    user_data = await state.get_data()
    diagnostika_id = user_data.get("diagnostika_id")
    old_name = user_data.get("old_name")

    if new_name.lower() == old_name.lower():
        await message.answer(
            "⚠️ Siz oldingi diagnostika nomini kiritdingiz!\n\n"
            "❗️ Iltimos, boshqa nom kiriting:",
            reply_markup=admin_back_menu
        )
        return

    updated_diagnostika = await update_diagnostika(diagnostika_id, name=new_name)

    if updated_diagnostika:
        text, keyboard = await get_diagnostika_detail_buttons(diagnostika_id)
        await message.answer(f"✅ Diagnostika nomi \"{new_name}\" ga o‘zgartirildi!\n\n{text}", reply_markup=keyboard)
    else:
        await message.answer("❌ Diagnostika nomini o‘zgartirishda xatolik yuz berdi.")

@dp.callback_query_handler(lambda call: call.data == "admin_diaginostika", state="*")
async def back_to_diagnostika_list(call: types.CallbackQuery):
    text, keyboard = await get_diagnostika_buttons()
    await call.message.edit_text(text, reply_markup=keyboard)
