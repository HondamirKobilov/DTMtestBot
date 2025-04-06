from aiogram.types import Message, ChatMemberUpdated, ContentType
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.storage import FSMContextProxy
from loader import dp
from utils.database.functions.f_refhistory import create_referral_history
from utils.database.functions.f_user import increment_user_referral_count
from utils.database.functions.f_group import get_group_by_chat_id
import json

@dp.message_handler(content_types=ContentType.WEB_APP_DATA, state="*")
async def receive_diagnostika_id(message: Message, state: FSMContext):
    try:
        data = json.loads(message.web_app_data.data)
        diagnostika_id = data.get("diagnostika_id")
        print("✅ WebApp'dan keldi:", diagnostika_id)
        await state.update_data(diagnostika_id=diagnostika_id)
        await message.answer("✅ Diagnostika ID qabul qilindi!")
    except Exception as e:
        print("❌ WebApp data parsingda xatolik:", e)
        await message.answer("❌ Xatolik yuz berdi!")

@dp.chat_member_handler()
async def on_user_invited(event: ChatMemberUpdated):
    if event.new_chat_member.status == "member" and event.from_user.id != event.new_chat_member.user.id:
        inviter_id = event.from_user.id
        invited_id = event.new_chat_member.user.id
        group_id = event.chat.id
        group_title = event.chat.title

        # Guruhni tekshirish
        group = await get_group_by_chat_id(group_id)
        if not group:
            print(f"❌ Guruh '{group_title}' ({group_id}) bazada yo‘q.")
            return

        # Faqat taklif qilgan foydalanuvchi uchun state olib diagnostika_id ni olamiz
        inviter_state = dp.current_state(user=inviter_id)
        state_data: FSMContextProxy = await inviter_state.get_data()
        diagnostika_id = state_data.get("diagnostika_id")

        if not diagnostika_id:
            print("⚠️ diagnostika_id topilmadi. Web App orqali yuborilishi kerak.")
            return

        # Referralni yozish
        added = await create_referral_history(inviter_id, invited_id, int(diagnostika_id))
        if not added:
            print(f"⚠️ {invited_id} allaqachon {inviter_id} tomonidan shu diagnostikaga taklif qilingan.")
            return

        # Referral count ni oshirish
        new_count = await increment_user_referral_count(inviter_id)
        if new_count is not None:
            print(f"✅ {inviter_id} foydalanuvchi {group_title} guruhiga {invited_id} ni taklif qildi. Jami: {new_count}")
        else:
            print(f"⚠️ {inviter_id} foydalanuvchi bazada topilmadi.")
