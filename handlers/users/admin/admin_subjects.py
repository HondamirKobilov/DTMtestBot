from aiogram import types
from aiogram.dispatcher import FSMContext
from typer.cli import state
from keyboards.inline.inline_admin import get_subject_buttons, admin_back_menu, \
    get_subject_detail_buttons, admin_back_button, get_test_buttons, \
    get_diagnostika_list_buttons, get_confirm_delete_subject_buttons, get_delete_tests_confirmation_buttons, \
    get_delete_test_buttons
from loader import dp
from states.admin import AddSubjectState, EditMainSubjectState
from utils.database.functions.f_diagnostika import delete_diagnostika_subject_link
from utils.database.functions.f_questions import delete_tests_by_diagnostika_and_subject, \
    get_tests_by_diagnostika_and_subject, count_tests_by_diagnostika_and_subject
from utils.database.functions.f_subject import get_subject_by_id, create_subject, get_all_subjects, update_subject, \
    delete_subject

@dp.callback_query_handler(lambda call: call.data == "admin_subjects", state="*")
async def show_main_subjects(call: types.CallbackQuery):
    text, keyboard = await get_subject_buttons()
    await call.message.edit_text(text, reply_markup=keyboard)

@dp.callback_query_handler(lambda call: call.data == "admin_add_subject", state="*")
async def ask_for_subject_name(call: types.CallbackQuery, state: FSMContext):
    await call.message.edit_text("📌 Iltimos, yangi fan nomini kiriting:", reply_markup=admin_back_menu)
    await state.set_state(AddSubjectState.waiting_for_subject_name)


@dp.message_handler(state=AddSubjectState.waiting_for_subject_name)
async def save_subject_name(message: types.Message, state: FSMContext):
    subject_name = message.text.strip()
    if not subject_name:
        await message.answer("⚠️ Fan nomi bo‘sh bo‘lishi mumkin emas! Iltimos, qaytadan kiriting:",
                             reply_markup=admin_back_menu)
        return
    existing_subjects = await get_all_subjects()
    existing_names = {subject.name.lower() for subject in existing_subjects}
    if subject_name.lower() in existing_names:
        await message.answer(f"❌ '{subject_name}' fani allaqachon mavjud! Boshqa nom kiriting:",
                             reply_markup=admin_back_menu)
        return
    await create_subject(subject_name)
    text, keyboard = await get_subject_buttons()
    await message.answer(f"✅ '{subject_name}' fani muvaffaqiyatli qo‘shildi!\n\n{text}", reply_markup=keyboard)
    await state.finish()
print("sssssss")
@dp.callback_query_handler(lambda call: call.data.startswith("admin_subject:"), state="*")
async def show_subject_details(call: types.CallbackQuery):
    subject_id = int(call.data.replace("admin_subject:", ""))
    text, keyboard = await get_subject_detail_buttons(subject_id)
    await call.message.edit_text(text, reply_markup=keyboard)

@dp.callback_query_handler(lambda call: call.data.startswith("admin_edit_subject_name:"), state="*")
async def ask_for_new_subject_name(call: types.CallbackQuery, state: FSMContext):
    subject_id = call.data.replace("admin_edit_subject_name:", "").strip()
    if not subject_id.isdigit():
        await call.answer("❌ Xatolik: Fan ID noto‘g‘ri!", show_alert=True)
        return
    subject_id = int(subject_id)
    subject = await get_subject_by_id(subject_id)
    if not subject:
        await call.answer("❌ Fan topilmadi!", show_alert=True)
        return
    await state.update_data(subject_id=subject_id)
    await call.message.edit_text(f"📌 Yangi nomni kiriting: (Joriy nom: {subject.name})", reply_markup=admin_back_menu)
    await state.set_state(EditMainSubjectState.waiting_for_new_name)

@dp.message_handler(state=EditMainSubjectState.waiting_for_new_name)
async def save_new_main_subject_name(message: types.Message, state: FSMContext):
    new_name = message.text.strip()
    if not new_name:
        await message.answer("⚠️ Fan nomi bo‘sh bo‘lishi mumkin emas! Iltimos, qaytadan kiriting:")
        return
    user_data = await state.get_data()
    subject_id = user_data.get("subject_id")
    subject = await get_subject_by_id(subject_id)
    existing_subjects = await get_all_subjects()
    existing_names = {subject.name.lower() for subject in existing_subjects}
    if new_name.lower() == subject.name.lower():
        await message.answer("⚠️ Bu oldingi nom edi, yangi nom kiriting:", reply_markup=admin_back_button())
        return
    if new_name.lower() in existing_names:
        await message.answer(f"❌ '{new_name}' fani allaqachon mavjud! Boshqa nom kiriting:", reply_markup=admin_back_button())
        return
    updated_subject = await update_subject(subject_id, name=new_name)
    if updated_subject:
        text, keyboard = await get_subject_detail_buttons(subject_id)
        await message.answer(f"✅ Fan nomi '{new_name}' ga muvaffaqiyatli o‘zgartirildi!\n\n{text}", reply_markup=keyboard)
    else:
        await message.answer("❌ Fan nomini o‘zgartirishda xatolik yuz berdi.")


@dp.callback_query_handler(lambda call: call.data.startswith("toggle_subject_compulsory:"), state="*")
async def toggle_subject_compulsory(call: types.CallbackQuery):
    subject_id = int(call.data.split(":")[1])
    subject = await get_subject_by_id(subject_id)
    if subject:
        new_status = not subject.is_compulsory_subject
        await update_subject(subject_id, is_compulsory_subject=new_status)
        await call.answer(f"Fan {'majburiy' if new_status else 'majburiy emas'} holatiga o‘zgartirildi")
    text, keyboard = await get_subject_detail_buttons(subject_id)
    await call.message.edit_text(text, reply_markup=keyboard)

@dp.callback_query_handler(lambda call: call.data.startswith("toggle_subject_foreign:"), state="*")
async def toggle_subject_foreign(call: types.CallbackQuery):
    subject_id = int(call.data.split(":")[1])
    subject = await get_subject_by_id(subject_id)
    if subject:
        new_status = not subject.is_foreign_language
        await update_subject(subject_id, is_foreign_language=new_status)
        await call.answer(f"Fan {'chet tili' if new_status else 'chet tili emas'} holatiga o‘zgartirildi")
    text, keyboard = await get_subject_detail_buttons(subject_id)
    await call.message.edit_text(text, reply_markup=keyboard)

@dp.callback_query_handler(lambda call: call.data.startswith("confirm_delete_subject:"), state="*")
async def confirm_delete_subject(call: types.CallbackQuery):
    subject_id = int(call.data.replace("confirm_delete_subject:", ""))
    text, keyboard = await get_confirm_delete_subject_buttons(subject_id)
    await call.message.edit_text(text, reply_markup=keyboard)

@dp.callback_query_handler(lambda call: call.data.startswith("delete_subject:"), state="*")
async def delete_subject_handler(call: types.CallbackQuery):
    subject_id = int(call.data.replace("delete_subject:", ""))
    deleted = await delete_subject(subject_id)
    if deleted:
        text, keyboard = await get_subject_buttons()
        await call.message.edit_text(f"✅ Fan muvaffaqiyatli o‘chirildi!\n\n{text}", reply_markup=keyboard)
    else:
        await call.answer("❌ Xatolik: Fanni o‘chirishda muammo yuz berdi!", show_alert=True)

@dp.callback_query_handler(lambda call: call.data.startswith("admin_subject_test:"), state="*")
async def show_diagnostika_list(call: types.CallbackQuery):
    subject_id = int(call.data.replace("admin_subject_test:", ""))
    text, keyboard = await get_diagnostika_list_buttons(subject_id)
    await call.message.edit_text(text, reply_markup=keyboard)

@dp.callback_query_handler(lambda call: call.data.startswith("admin_diagnostika_details:"), state="*")
async def show_tests_for_diagnostika(call: types.CallbackQuery):
    data_parts = call.data.split(":")
    diagnostika_id = int(data_parts[1])
    subject_id = int(data_parts[2])
    text, keyboard = await get_test_buttons(subject_id, diagnostika_id)
    await call.message.edit_text(text, reply_markup=keyboard)

@dp.callback_query_handler(lambda call: call.data.startswith("admin_delete_tests:"), state="*")
async def confirm_delete_tests(call: types.CallbackQuery):
    data_parts = call.data.split(":")
    subject_id = int(data_parts[1])
    diagnostika_id = int(data_parts[2])
    keyboard = await get_delete_test_buttons(subject_id, diagnostika_id)
    await call.message.edit_text("⚠️ Qaysi testlarni o‘chirmoqchisiz?", reply_markup=keyboard)


@dp.callback_query_handler(lambda call: call.data.startswith("confirm_delete_tests:"))
async def confirm_delete_tests(call: types.CallbackQuery):
    data_parts = call.data.split(":")
    test_type = data_parts[1]  # "normal" yoki "mandatory"
    subject_id = int(data_parts[2])
    diagnostika_id = int(data_parts[3])
    keyboard = get_delete_tests_confirmation_buttons(test_type, subject_id, diagnostika_id)
    text = "⚠️ Rostdan ham "
    text += "majburiy" if test_type == "mandatory" else "asosiy"
    text += " testlarni o‘chirmoqchimisiz?"
    await call.message.edit_text(text, reply_markup=keyboard)

@dp.callback_query_handler(lambda call: call.data.startswith("delete_tests:"), state="*")
async def delete_tests_for_diagnostika(call: types.CallbackQuery):
    data_parts = call.data.split(":")
    test_type = data_parts[1]  # "normal" yoki "mandatory"
    subject_id = int(data_parts[2])
    diagnostika_id = int(data_parts[3])
    deleted = await delete_tests_by_diagnostika_and_subject(diagnostika_id, subject_id, is_mandatory=(test_type == "mandatory"))
    if not deleted:
        await call.answer(f"❌ {test_type.capitalize()} testlar allaqachon o‘chirilgan yoki mavjud emas!", show_alert=True)
        return
    remaining_tests = await count_tests_by_diagnostika_and_subject(diagnostika_id, subject_id)
    if remaining_tests == 0:
        await delete_diagnostika_subject_link(diagnostika_id, subject_id)
    await call.answer(f"✅ {test_type.capitalize()} testlar muvaffaqiyatli o‘chirildi!", show_alert=True)
    text, keyboard = await get_diagnostika_list_buttons(subject_id)
    await call.message.edit_text(f"✅ {test_type.capitalize()} testlar o‘chirildi!\n\n{text}", reply_markup=keyboard)

@dp.callback_query_handler(lambda call: call.data.startswith("cancel_delete_tests:"))
async def cancel_delete_tests(call: types.CallbackQuery):
    data_parts = call.data.split(":")
    subject_id = int(data_parts[1])
    diagnostika_id = int(data_parts[2])
    text, keyboard = await get_test_buttons(subject_id, diagnostika_id)
    await call.message.edit_text(text, reply_markup=keyboard)

