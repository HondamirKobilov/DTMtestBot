from aiogram.types import (
    InlineKeyboardMarkup as IKM,
    InlineKeyboardButton as IKB
)
from data.config import channels_manager
from data.texts import const_button, lang_button
from utils.database.functions.f_diagnostika import get_all_diagnostikas, get_diagnostika_by_id, \
    is_diagnostika_linked_to_subject, get_tests_by_diagnostika_and_subject, count_questions_for_diagnostika, \
    count_diagnostikas_by_subject
from utils.database.functions.f_questions import  count_tests_by_diagnostika_and_subject
from utils.database.functions.f_subject import get_all_subjects, get_subject_by_id


def inline_admin_keyboards(*args):
    return [IKB(text=const_button(i), callback_data=i) for i in args]


admin_main_menu = IKM(
    row_width=1,
    inline_keyboard=[
        inline_admin_keyboards("admin_send_message"),
        inline_admin_keyboards("admin_statistics"),
        inline_admin_keyboards("admin_manage_channels"),
        inline_admin_keyboards("admin_subjects"),
        inline_admin_keyboards("admin_diaginostika")
    ]
)

admin_back_menu = IKM(
    row_width=1,
    inline_keyboard=[
        inline_admin_keyboards("admin_back")
    ]
)


def channels_menu():
    keyboard = IKM(row_width=1)
    channels = channels_manager.get_channels()
    for i, channel in enumerate(channels, start=1):
        keyboard.insert(IKB(f"{i}. {channel['title']}", callback_data=f"admin_edit_{channel['id']}"))

    keyboard.add(IKB(const_button("admin_add_channel"), callback_data="admin_add_channel"))
    keyboard.add(IKB(const_button("admin_back"), callback_data="admin_back"))
    return keyboard


def edit_channel_menu(channel_id):
    keyboard = IKM(row_width=2)
    keyboard.insert(IKB(const_button("admin_edit"), callback_data=f"admin_modify_{channel_id}"))
    keyboard.insert(IKB(const_button("admin_delete"), callback_data=f"admin_delete_channel_{channel_id}"))
    keyboard.add(IKB(const_button("admin_back"), callback_data="admin_back_to_channels"))
    return keyboard

def edit_variant_menu(variant_id):
    markup = IKM(row_width=1)
    markup.insert(IKB(const_button("admin_delete"), callback_data=f"admin_variant_delete_{variant_id}"))
    markup.add(IKB(text="⬅ Ortga", callback_data="admin_back_to_subjects"))

    return markup
def admin_back_button(callback_data: str = "admin_subjects"):
    keyboard = IKM(row_width=1)
    keyboard.add(IKB(text="⬅ Ortga", callback_data=callback_data))
    return keyboard

def kb_admin_subject_language():
    kb = IKM(
        row_width=3
    )
    for lang, lang_text in lang_button.items():
        kb.insert(IKB(text=lang_text, callback_data=f'admin_subject_lang_{lang}'))
    kb.add(IKB(text="⬅ Ortga", callback_data="admin_back_to_subjects"))
    return kb

def subject_menu():
    keyboard = IKM(row_width=1)
    keyboard.add(
        IKB(text="📚 Asosiy fanlar", callback_data="admin_main_subjects"),
        IKB(text="⬅ Ortga", callback_data="admin_back")
    )
    return keyboard


async def get_subject_buttons():
    subjects = await get_all_subjects()
    keyboard = IKM(row_width=2)
    if not subjects:
        keyboard.add(IKB(const_button("admin_add_subject"), callback_data="admin_add_subject"))
        keyboard.add(IKB(text="🔙 Ortga", callback_data="admin_back"))
        return "❌ Hali fanlar mavjud emas.", keyboard
    for subject in subjects:
        keyboard.insert(IKB(text=subject.name, callback_data=f"admin_subject:{subject.id}"))
    keyboard.add(IKB(const_button("admin_add_subject"), callback_data="admin_add_subject"))
    keyboard.add(IKB(text="🔙 Ortga", callback_data="admin_back"))
    return "📚 Fanlar ro‘yxati:", keyboard


async def get_subject_detail_buttons(subject_id: int):
    subject = await get_subject_by_id(subject_id)
    diagnostika_count = await count_diagnostikas_by_subject(subject_id)
    keyboard = IKM(row_width=2)
    if subject:
        compulsory_text = "✅ Majburiy" if subject.is_compulsory_subject else "❌ Majburiy emas"
        foreign_text = "✅ Chet tili" if subject.is_foreign_language else "❌ Chet tili emas"
        keyboard.add(
            IKB(text=compulsory_text, callback_data=f"toggle_subject_compulsory:{subject.id}"),
            IKB(text=foreign_text, callback_data=f"toggle_subject_foreign:{subject.id}")
        )
        keyboard.add(
            IKB(text=f"✏️ {subject.name}", callback_data=f"admin_edit_subject_name:{subject.id}"),
            IKB(text=f"📝 Diagnostika ({diagnostika_count} ta)", callback_data=f"admin_subject_test:{subject.id}")  # ✅ Diagnostika soni chiqariladi
        )
        keyboard.add(
            IKB(text="🗑 O‘chirish", callback_data=f"confirm_delete_subject:{subject.id}"),
            IKB(text="🔙 Ortga", callback_data="admin_subjects")
        )
    return f"📌 Tanlangan fan: {subject.name}", keyboard

async def get_confirm_delete_subject_buttons(subject_id: int):
    keyboard = IKM(row_width=2)
    keyboard.row(
        IKB(text="✅ Ha", callback_data=f"delete_subject:{subject_id}"),
        IKB(text="❌ Yo‘q", callback_data=f"admin_subject:{subject_id}")
    )
    return "⚠️ Rostan ham shu fanni o‘chirmoqchimisiz?", keyboard


async def get_test_buttons(subject_id: int, diagnostika_id: int):
    tests = await get_tests_by_diagnostika_and_subject(diagnostika_id, subject_id)
    subject = await get_subject_by_id(subject_id)
    keyboard = IKM(row_width=1)
    text = f"📌 Diagnostika va fan bo‘yicha testni o‘chirishingiz mumkin:\n\n"
    if tests:
        keyboard.add(IKB(text="🗑 Testni o‘chirish", callback_data=f"admin_delete_tests:{subject_id}:{diagnostika_id}"))
    else:
        text += "❌ Hali testlar mavjud emas."
    existing_tests = await count_questions_for_diagnostika(diagnostika_id, subject_id)
    if existing_tests < 30 and not tests:
        keyboard.add(IKB(text="➕ Test qo‘shish", callback_data=f"admin_add_test:{subject_id}:{diagnostika_id}"))
    if subject.is_compulsory_subject:
        keyboard.add(IKB(text="➕ Majburiy test qo‘shish",
                         callback_data=f"admin_add_mandatory_test:{subject_id}:{diagnostika_id}"))
    keyboard.add(IKB(text="🔙 Ortga", callback_data=f"admin_subject_test:{subject_id}"))
    return text, keyboard


async def get_delete_test_buttons(subject_id: int, diagnostika_id: int):
    mandatory_tests = await get_tests_by_diagnostika_and_subject(diagnostika_id, subject_id, is_mandatory=True)
    normal_tests = await get_tests_by_diagnostika_and_subject(diagnostika_id, subject_id, is_mandatory=False)
    keyboard = IKM(row_width=1)
    if normal_tests:
        keyboard.add(IKB(text="🗑 Asosiy testlarni o‘chirish",
                         callback_data=f"confirm_delete_tests:normal:{subject_id}:{diagnostika_id}"))
    if mandatory_tests:
        keyboard.add(IKB(text="🗑 Majburiy testlarni o‘chirish",
                         callback_data=f"confirm_delete_tests:mandatory:{subject_id}:{diagnostika_id}"))
    keyboard.add(IKB(text="🔙 Ortga", callback_data=f"admin_subject_test:{subject_id}"))
    return keyboard

async def get_diagnostika_buttons():
    diagnostikalar = await get_all_diagnostikas()
    keyboard = IKM(row_width=2)
    if not diagnostikalar:
        keyboard.add(IKB(text="➕ Diagnostika qo‘shish", callback_data="admin_add_diagnostika"))
        keyboard.add(IKB(text="🔙 Ortga", callback_data="admin_back"))
        return "❌ Hali diagnostikalar mavjud emas.", keyboard
    for diagnostika in diagnostikalar:
        keyboard.insert(IKB(text=diagnostika.name, callback_data=f"admin_diagnostika:{diagnostika.id}"))
    keyboard.add(IKB(text="➕ Diagnostika qo‘shish", callback_data="admin_add_diagnostika"))
    keyboard.add(IKB(text="🔙 Ortga", callback_data="admin_back"))
    return "📋 Diagnostika ro‘yxati:", keyboard

async def get_diagnostika_detail_buttons(diagnostika_id: int):
    diagnostika = await get_diagnostika_by_id(diagnostika_id)
    keyboard = IKM(row_width=2)
    if diagnostika:
        keyboard.add(
            IKB(text="✏️ Tahrirlash", callback_data=f"admin_edit_diagnostika:{diagnostika.id}"),
            IKB(text="🗑 O‘chirish", callback_data=f"confirm_delete_diagnostika:{diagnostika.id}")
        )
        keyboard.add(IKB(text="🔙 Ortga", callback_data="admin_diaginostika"))
    return f"📌 Tanlangan diagnostika: {diagnostika.name}", keyboard

async def get_confirm_delete_diaginostika_buttons(diagnostika_id: int):
    keyboard = IKM(row_width=2)
    keyboard.row(
        IKB(text="✅ Ha", callback_data=f"delete_diagnostika:{diagnostika_id}"),
        IKB(text="❌ Yo‘q", callback_data=f"admin_diagnostika:{diagnostika_id}")
    )
    return "⚠️ Rostan ham shu diagnostikani o‘chirmoqchimisiz?", keyboard

async def get_diagnostika_list_buttons(subject_id: int):
    subject = await get_subject_by_id(subject_id)
    diagnostikalar = await get_all_diagnostikas()
    keyboard = IKM(row_width=2)
    if not diagnostikalar:
        keyboard.add(IKB(text="🔙 Ortga", callback_data=f"admin_back"))
        return f"❌ {subject.name} faniga oid diagnostikalar mavjud emas.", keyboard
    for diagnostika in diagnostikalar:
        is_linked = await is_diagnostika_linked_to_subject(diagnostika.id, subject_id)
        test_count = await count_tests_by_diagnostika_and_subject(diagnostika.id, subject_id)
        status_icon = "✅" if is_linked else "❌"
        keyboard.insert(
            IKB(
                text=f"{status_icon} {diagnostika.name} ({test_count} ta test)",
                callback_data=f"admin_diagnostika_details:{diagnostika.id}:{subject_id}"
            )
        )
    keyboard.add(IKB(text="🔙 Ortga", callback_data=f"admin_subject:{subject_id}"))
    return f"📋 {subject.name} fan bo'yicha diagnostika ro‘yxati:", keyboard

async def diagnostika_test(diagnostika_id: int):
    diagnostika = await get_diagnostika_by_id(diagnostika_id)
    keyboard = IKM(row_width=2)
    if diagnostika:
        keyboard.add(
            IKB(text="📝 Testlar", callback_data=f"admin_diagnostika_tests:{diagnostika.id}"),
            IKB(text="✏️ Tahrirlash", callback_data=f"admin_edit_diagnostika:{diagnostika.id}")
        )
        keyboard.add(
            IKB(text="🗑 O‘chirish", callback_data=f"confirm_delete_diagnostika:{diagnostika.id}"),
            IKB(text="🔙 Ortga", callback_data="admin_subjects")
        )
    return f"📌 Tanlangan diagnostika: {diagnostika.name}", keyboard

def get_delete_tests_confirmation_buttons(test_type: str, subject_id: int, diagnostika_id: int) -> IKM:
    keyboard = IKM(row_width=2)
    keyboard.add(
        IKB(text="✅ Ha, o‘chirish", callback_data=f"delete_tests:{test_type}:{subject_id}:{diagnostika_id}"),
        IKB(text="❌ Yo‘q, bekor qilish", callback_data=f"cancel_delete_tests:{subject_id}:{diagnostika_id}")
    )
    return keyboard
