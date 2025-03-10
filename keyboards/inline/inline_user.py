from aiogram.types import InlineKeyboardMarkup as IKM, InlineKeyboardButton as IKB, WebAppInfo
from data.config import USERNAME_START, WEB_APP_URL
from data.consts import uzbekistan_regions
from data.texts import lang_button, button
language_picker = IKM(
    inline_keyboard=[
        [
            IKB(text=lang_button["uz"], callback_data='lang:uz'),
            IKB(text=lang_button["ru"], callback_data='lang:ru'),
        ]
    ]
)



def kb_subject_subjects(subjects, lang):
    kb = IKM(
        row_width=2
    )
    for subject in subjects:
        kb.insert(IKB(text=subject.name, callback_data=f"subject_id:{subject.id}"))
    kb.add(IKB(text=button('user_back', lang), callback_data="user_back_to_subject"))
    return kb


def kb_subject_variants(variants, language):
    kb = IKM(
        row_width=2
    )
    for variant in variants:
        kb.insert(IKB(text=f"{variant.variant_id}-variant", callback_data=f"variant_id:{variant.variant_id}"))
    kb.add(IKB(text=button('user_back', language), callback_data="user_back_to_lang_subject"))
    return kb




def kb_variant_answer(variant_id, lang):
    markup = IKM()
    markup.add(IKB(text=button("user_confirmation", lang), callback_data=f"user_variant_confirm_{variant_id}"),
               IKB(text=button('user_retype_answer', lang), callback_data=f"user_variant_retry_{variant_id}"))
    markup.add(IKB(text=button('user_cancel_answer', lang), callback_data=f"user_variant_cancel_{variant_id}"))
    return markup


def kb_subject_menu(variant_id, lang):
    kb = IKM(
        row_width=1
    )
    kb.insert(IKB(text=button("user_check_answer", lang), url=f"{USERNAME_START}exam_{variant_id}"))
    kb.insert(IKB(text=button("user_share_variant", lang), switch_inline_query=f"share {variant_id}"))
    kb.add(IKB(text=button("user_back", lang), callback_data="user_back_to_langs"))
    return kb


def kb_share_menu(lang):
    kb = IKM(
        row_width=1
    )
    kb.insert(IKB(text=button("user_get_subject", lang), url=f"{USERNAME_START}share"))
    return kb


def kb_subject_share_menu(subject_id, lang):
    kb = IKM(
        row_width=1
    )
    kb.insert(IKB(text=button("user_check_answer", lang), url=f"{USERNAME_START}exam_{subject_id}"))
    return kb


def region_picker(lang):
    kb = IKM(row_width=2)
    for i, region in enumerate(uzbekistan_regions[lang]):
        kb.insert(IKB(region['name'], callback_data=f"region:{i}"))

    return kb


def district_picker(region, lang):
    kb = IKM(row_width=2)
    for i, district in enumerate(uzbekistan_regions[lang][region]['districts']):
        kb.insert(IKB(district, callback_data=f"district:{i}"))
    return kb

def back_button(lang: str) -> IKM:
    return IKM().add(
        IKB(
            text=button("user_back", lang=lang),
            callback_data="user_back_to_home"
        )
    )

def inline_keyboard_markup():
    keyboard = IKM(row_width=2)
    keyboard.add(
        IKB("Tasdiqlash ✅", callback_data="confirm_answers"),
        IKB("Qayta yuborish 🔄", callback_data="resend_answers")
    )
    keyboard.add(
        IKB("Ortga 🔙", callback_data="go_back")
    )
    return keyboard

def get_interactive_menu_keyboard():
    keyboard = IKM()
    keyboard.add(IKB("Web app", web_app=WebAppInfo(url=f"{WEB_APP_URL}")))
    return keyboard