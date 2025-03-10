from aiogram import types
from aiogram.dispatcher import FSMContext
from keyboards.inline.inline_admin import get_diagnostika_buttons, admin_back_menu, get_diagnostika_detail_buttons, get_confirm_delete_diaginostika_buttons
from loader import dp
from states.admin import AddDiagnostikaState, EditDiagnostikaState
from utils.database.functions.f_diagnostika import create_diagnostika, delete_diagnostika, get_diagnostika_by_id, \
    update_diagnostika
from datetime import datetime


@dp.callback_query_handler(lambda call: call.data == "admin_diaginostika", state="*")
async def admin_diagnostika_handler(call: types.CallbackQuery):
    text, keyboard = await get_diagnostika_buttons()
    await call.message.edit_text(text, reply_markup=keyboard)

@dp.callback_query_handler(lambda call: call.data == "admin_add_diagnostika", state="*")
async def ask_diagnostika_name(call: types.CallbackQuery, state: FSMContext):
    await call.message.edit_text("✏️ Iltimos, yangi diagnostika nomini kiriting:", reply_markup=admin_back_menu)
    await AddDiagnostikaState.waiting_for_name.set()

@dp.message_handler(state=AddDiagnostikaState.waiting_for_name)
async def process_diagnostika_name(message: types.Message, state: FSMContext):
    diagnostika_name = message.text.strip()
    await state.update_data(diagnostika_name=diagnostika_name)
    await message.answer("📅 Iltimos, tugash vaqtini kiriting (YYYY-MM-DD HH:MM formatida):")
    await AddDiagnostikaState.waiting_for_finished_at.set()

@dp.message_handler(state=AddDiagnostikaState.waiting_for_finished_at)
async def process_diagnostika_finished_at(message: types.Message, state: FSMContext):
    finished_at_text = message.text.strip()
    try:
        finished_at = datetime.strptime(finished_at_text, "%Y-%m-%d %H:%M")
    except ValueError:
        await message.answer("⚠️ Noto‘g‘ri format! Tugash vaqtini YYYY-MM-DD HH:MM formatida kiriting.")
        return
    data = await state.get_data()
    diagnostika_name = data.get("diagnostika_name")
    await create_diagnostika(diagnostika_name, finished_at)
    text, keyboard = await get_diagnostika_buttons()
    await message.answer(f"✅ Diagnostika \"{diagnostika_name}\" muvaffaqiyatli qo‘shildi!\n\n{text}",
                         reply_markup=keyboard)

@dp.callback_query_handler(lambda call: call.data.startswith("admin_diagnostika:"), state="*")
async def show_diagnostika_details(call: types.CallbackQuery):
    """📋 Diagnostika tafsilotlarini ko‘rsatish"""
    diagnostika_id = int(call.data.split(":")[1])  # ID ajratib olish
    text, keyboard = await get_diagnostika_detail_buttons(diagnostika_id)
    await call.message.edit_text(text, reply_markup=keyboard)


@dp.callback_query_handler(lambda call: call.data.startswith("toggle_diagnostika_status:"), state="*")
async def toggle_diagnostika_status(call: types.CallbackQuery, state: FSMContext):
    diagnostika_id = int(call.data.replace("toggle_diagnostika_status:", ""))
    diagnostika = await get_diagnostika_by_id(diagnostika_id)

    if not diagnostika:
        await call.answer("❌ Diagnostika topilmadi!", show_alert=True)
        return

    # ✅ Statusni o‘zgartirish (agar True bo‘lsa False, False bo‘lsa True bo‘lsin)
    new_status = not diagnostika.status

    if new_status:
        # ✅ Agar diagnostika yoqilsa, tugash vaqtini so‘rash
        await state.update_data(diagnostika_id=diagnostika_id)
        await call.message.edit_text("📅 Qaysi vaqtgacha qo‘yishni xohlaysiz? (YYYY-MM-DD HH:MM formatida kiriting):")
        await EditDiagnostikaState.waiting_for_finished_at.set()
    else:
        # ✅ Agar diagnostika o‘chirilsa, statusni yangilash
        await update_diagnostika(diagnostika_id, status=False)
        text, keyboard = await get_diagnostika_detail_buttons(diagnostika_id)
        await call.message.edit_text(text, reply_markup=keyboard)
        await call.answer("✅ Diagnostika o‘chirildi!")
@dp.message_handler(state=EditDiagnostikaState.waiting_for_finished_at)
async def process_new_finished_at(message: types.Message, state: FSMContext):
    finished_at_text = message.text.strip()
    try:
        finished_at = datetime.strptime(finished_at_text, "%Y-%m-%d %H:%M")
    except ValueError:
        await message.answer("⚠️ Noto‘g‘ri format! Tugash vaqtini YYYY-MM-DD HH:MM formatida kiriting.")
        return

    data = await state.get_data()
    diagnostika_id = data.get("diagnostika_id")

    # ✅ Diagnostikani yangilash
    await update_diagnostika(diagnostika_id, status=True, finished_at=finished_at)

    # ✅ Yangi ma'lumotlarni chiqarish
    text, keyboard = await get_diagnostika_detail_buttons(diagnostika_id)
    await message.answer(f"✅ Diagnostika yangilandi!\n\n{text}", reply_markup=keyboard)

    await state.finish()

@dp.callback_query_handler(lambda call: call.data.startswith("confirm_delete_diagnostika:"), state="*")
async def confirm_delete_diagnostika(call: types.CallbackQuery):
    """🗑 Diagnostikani o‘chirishni tasdiqlash"""
    diagnostika_id = int(call.data.split(":")[1])  # ID ajratib olish
    text, keyboard = await get_confirm_delete_diaginostika_buttons(diagnostika_id)
    await call.message.edit_text(text, reply_markup=keyboard)

@dp.callback_query_handler(lambda call: call.data.startswith("delete_diagnostika:"), state="*")
async def delete_diagnostika_handler(call: types.CallbackQuery):
    """❌ Diagnostikani o‘chirish"""
    diagnostika_id = int(call.data.split(":")[1])  # ID ajratib olish

    # Diagnostika mavjudligini tekshirish
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


@dp.callback_query_handler(lambda call: call.data.startswith("admin_edit_diagnostika:"), state="*")
async def ask_for_new_diagnostika_name(call: types.CallbackQuery, state: FSMContext):
    diagnostika_id = int(call.data.replace("admin_edit_diagnostika:", ""))
    diagnostika = await get_diagnostika_by_id(diagnostika_id)

    if not diagnostika:
        await call.answer("❌ Diagnostika topilmadi!", show_alert=True)
        return

    # ✅ Statusni belgilash
    status_emoji = "🟡" if diagnostika.status else "🔴"

    await state.update_data(diagnostika_id=diagnostika_id, old_name=diagnostika.name)

    await call.message.edit_text(
        f"📌 Yangi diagnostika nomini kiriting: (Joriy nom: {diagnostika.name})\n\n"
        f"{status_emoji} Status",
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
