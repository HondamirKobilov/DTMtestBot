from aiogram import types
from aiogram.dispatcher import FSMContext
from keyboards.inline.inline_admin import referral_update_buttons, referral_action_buttons, admin_back_menu
from loader import dp
from states.admin import ReferralStates
from utils.database.functions.f_ref import view_referral_count, set_referral_count

@dp.callback_query_handler(lambda call: call.data == "admin_ref", state="*")
async def show_referral_count(call: types.CallbackQuery):
    count = await view_referral_count()
    if count:
        text = f"📊 <b>Referal soni:</b> {count} ta"
        await call.message.edit_text(
            text,
            reply_markup=referral_update_buttons(),
            parse_mode="HTML"
        )
    else:
        text = "📭 <b>Hali referal soni qo‘shilmagan</b>"
        await call.message.edit_text(
            text,
            reply_markup=referral_action_buttons(),
            parse_mode="HTML"
        )

@dp.callback_query_handler(lambda call: call.data == "admin_add_referral", state="*")
async def ask_referral_value(call: types.CallbackQuery, state: FSMContext):
    await call.message.edit_text("✏️ Yangi referal sonini kiriting:", reply_markup=admin_back_menu)
    await state.set_state(ReferralStates.waiting_for_new_count)

@dp.message_handler(state=ReferralStates.waiting_for_new_count)
async def save_referral_value(message: types.Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer("🚫 Iltimos, faqat butun son kiriting.")
        return
    value = int(message.text)
    await set_referral_count(value)
    await message.answer(f"✅ {value} ta referal saqlandi!", reply_markup=referral_update_buttons())
    await state.finish()

@dp.callback_query_handler(lambda call: call.data == "admin_change_referral", state="*")
async def ask_referral_edit_value(call: types.CallbackQuery, state: FSMContext):
    await call.message.edit_text("✏️ Yangi referal sonini kiriting:", reply_markup=admin_back_menu)
    await state.set_state(ReferralStates.waiting_for_edit_count)

@dp.message_handler(state=ReferralStates.waiting_for_edit_count)
async def edit_referral_value(message: types.Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer("🚫 Iltimos, faqat butun son kiriting.")
        return

    value = int(message.text)
    await set_referral_count(value)

    await message.answer(f"✅ Referal soni yangilandi: {value} ta", reply_markup=referral_update_buttons())
    await state.finish()