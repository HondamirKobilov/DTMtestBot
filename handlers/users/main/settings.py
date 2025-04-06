from typing import Union
from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from data.config import channels_manager
from data.consts import uzbekistan_regions
from data.texts import text, buttons, lang_button
from keyboards.default.default_user import *
from keyboards.inline.inline_user import district_picker, region_picker
from loader import dp, bot
from states.user import Dispatch
from utils.database.functions import f_user
from utils.database.models import User
from utils.misc import subscription


@dp.callback_query_handler(text_contains='lang:', state="*")
async def lang_picker(call: types.CallbackQuery, state: FSMContext):
    user_id = call.from_user.id
    language = call.data.replace("lang:", "")

    await f_user.update_user(user_id, language=language)
    await call.message.edit_text(
        text("user_register_name", language),
        reply_markup=None
    )


@dp.callback_query_handler(text_contains='region:', state="*")
async def lang_picker(call: types.CallbackQuery):
    user_id = call.from_user.id
    region = int(call.data.replace("region:", ""))
    user = await f_user.select_user(user_id)
    language = user.language

    await f_user.update_user(user_id, region=region)
    if user.district is not None:
        await user_settings_handler(call)
        return

    await call.message.edit_text(
        text("user_register_district", language),
        reply_markup=district_picker(region, language)
    )


@dp.callback_query_handler(text_contains='district:', state="*")
async def lang_picker(call: types.CallbackQuery):
    user_id = call.from_user.id
    district = int(call.data.replace("district:", ""))
    user = await f_user.select_user(user_id)
    language = user.language

    await f_user.update_user(user_id, district=district)
    if user.phone is not None:
        await user_settings_handler(call)
        return
    try:
        await call.message.delete()
    except:
        pass
    await call.message.answer(
        text("user_register_phone", language).format(user_phone_number=button("user_phone_number", language)),
        reply_markup=user_contact_menu(language)
    )


async def send_phone_request(user_id):
    user: User = await f_user.select_user(user_id)

    await bot.send_message(
        user_id,
        text("user_register_phone", user.language).format(
            user_phone_number=button("user_phone_number", user.language)
        ),
        reply_markup=user_contact_menu(user.language)
    )

async def check_status(user_id, lang):
    final_status = True
    chs = []
    for channel in channels_manager.get_channels():
        channel_id = channel.get("id")
        try:
            status = await subscription.check(
                user_id=user_id,
                channel=channel_id
            )
            final_status &= status
            if not status:
                chat = await bot.get_chat(channel_id)
                invite_link = await chat.export_invite_link()
                chs.append([InlineKeyboardButton(text=chat.title, url=invite_link)])
        except Exception as ex:
            print("check channels:", ex)
    chs.append([InlineKeyboardButton(text=button("user_check_subscribe", lang), callback_data=f"user_check_subs")])
    return final_status, chs

async def my_mind(message, state):
    user_id = message.from_user.id
    user = await f_user.select_user(user_id)
    lang = user.language

    status, keyboard = await check_status(user_id, lang)
    if isinstance(message, types.CallbackQuery):
        message = message.message

    if not status:
        await message.answer("❕", reply_markup=types.ReplyKeyboardRemove())
        await message.answer(
            text("user_subscribe_request", lang),
            reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard),
            disable_web_page_preview=True
        )
        return

    if user.referral_count is not None:
        await f_user.update_user(user_id, referral_count=0)
    else:
        await message.answer(text("user_start", lang), reply_markup=kb_main_menu(lang))

@dp.message_handler(content_types='contact', state="*")
async def user_phone_number_handler(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    user = await f_user.select_user(user_id)
    lang = user.language

    if message.contact.user_id != user_id:
        await send_phone_request(user_id)
        return

    ph = f"+{str(message.contact.phone_number).replace('+', '').replace(' ', '')}"
    await f_user.update_user(user_id, phone=ph)
    st = await state.get_state()
    if st == "Dispatch:user_settings":
        await user_settings_handler(message)
        return
    await my_mind(message, state)

@dp.callback_query_handler(text='user_check_subs', state="*")
async def user_check_subs_handler(call: types.CallbackQuery, state: FSMContext):
    user_id = call.from_user.id
    language = await f_user.select_user_language(user_id)
    try:
        await call.message.delete()
    except:
        pass
    await my_mind(call, state)

@dp.message_handler(Text(equals=buttons("user_settings")), state="*")
async def user_settings_handler(message: Union[types.Message, types.CallbackQuery]):
    user_id = message.from_user.id
    user: User = await f_user.select_user(user_id)
    settings_text = text("user_settings", user.language).format(
        fullname=user.fullname,
        phone=user.phone,
        region=uzbekistan_regions[user.language][user.region]['name'],
        district=uzbekistan_regions[user.language][user.region]['districts'][user.district]
    )
    if isinstance(message, types.Message):
        await message.answer(settings_text, reply_markup=user_settings_menu(user.language))
    else:
        try:
            await message.message.delete()
        except:
            pass
        await message.message.answer(settings_text, reply_markup=user_settings_menu(user.language))
    try:
        await Dispatch.user_settings.set()
    except:
        pass


@dp.message_handler(state=Dispatch.user_settings)
async def user_choose_settings_handler(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    user: User = await f_user.select_user(user_id)
    if message.text in buttons("user_settings_language"):
        lang = 'uz' if message.text == lang_button["uz"] else 'ru'
        await f_user.update_user(user_id, language=lang)
        await user_settings_handler(message)

    elif message.text in buttons("user_settings_phone"):
        await f_user.update_user(user_id, phone=None)
        await send_phone_request(user_id)
    elif message.text in buttons("user_settings_name"):
        await f_user.update_user(user_id, fullname=None)
        await message.answer(text("user_register_name", user.language), reply_markup=types.ReplyKeyboardRemove())
    elif message.text in buttons("user_settings_region"):
        await f_user.update_user(user_id, region=None)
        await message.answer(text("user_register_region", user.language), reply_markup=region_picker(user.language))
    elif message.text in buttons("user_settings_district"):
        await f_user.update_user(user_id, district=None)
        await message.answer(
            text("user_register_district", user.language),
            reply_markup=district_picker(user.region, user.language)
        )
