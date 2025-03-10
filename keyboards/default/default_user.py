from aiogram.types import ReplyKeyboardMarkup as RKM, KeyboardButton, WebAppInfo

from data.config import domen
from data.texts import button


def reply_keyboards(lang="uz", *args):
    return [KeyboardButton(text=button(i, lang)) for i in args]


def kb_main_menu(lang):
    return RKM(
        one_time_keyboard=True,
        resize_keyboard=True,
        keyboard=[
            reply_keyboards(lang, "user_settings")
        ]
    )

def kb_solve_subject_menu(lang):
    return RKM(
        one_time_keyboard=True,
        resize_keyboard=True,
        keyboard=[
            reply_keyboards(lang, "user_subject_subject"),
            reply_keyboards(lang, "user_full_subject"),
            reply_keyboards(lang, "user_back"),
        ]
    )


def kb_subject_subject_menu(lang):
    return RKM(
        one_time_keyboard=True,
        resize_keyboard=True,
        keyboard=[
            reply_keyboards(lang, "user_get_subject"),
            reply_keyboards(lang, "user_check_answer"),
            reply_keyboards(lang, "user_2_back"),
        ]
    )


def user_settings_menu(lang):
    return RKM(
        one_time_keyboard=True,
        resize_keyboard=True,
        keyboard=[
            reply_keyboards(lang, "user_settings_name", "user_settings_phone"),
            reply_keyboards(lang, "user_settings_region", "user_settings_district"),
            reply_keyboards(lang, "user_settings_language"),
            reply_keyboards(lang, "user_back")
        ]
    )


def user_contact_menu(lang):
    return RKM(
        one_time_keyboard=True,
        resize_keyboard=True,
        keyboard=[
            [KeyboardButton(button("user_phone_number", lang), request_contact=True)],
        ]
    )


def user_back_menu(lang):
    return RKM(
        one_time_keyboard=True,
        resize_keyboard=True,
        keyboard=[
            reply_keyboards(lang, "user_3_back")
        ]
    )


def back_button_default(lang: str) -> RKM:
    kb = RKM(resize_keyboard=True, one_time_keyboard=True)
    kb.add(
        KeyboardButton(text=button("user_back", lang=lang))  # Tugma matni
    )
    return kb