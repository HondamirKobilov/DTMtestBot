from aiogram import types
from aiogram.dispatcher.handler import CancelHandler
from aiogram.dispatcher.middlewares import BaseMiddleware
from aiogram.types import InlineKeyboardMarkup
from data.config import ADMINS, toshkent_now
from data.texts import const_text, text
from handlers.users.main.settings import user_settings_handler, send_phone_request
from keyboards.inline.inline_user import language_picker, region_picker, district_picker
from loader import bot
from middlewares.misc import check_status
from utils.database.functions import f_user

class BigBrother(BaseMiddleware):
    async def on_pre_process_update(self, update: types.Update, data: dict):
        user_id = update.message.from_user.id if update.message else update.callback_query.from_user.id if update.callback_query else False
        if not user_id:
            return
        if update.message and "group" in update.message.chat.type:
            raise CancelHandler()
        if update.message:
            user_data = await f_user.select_user(user_id)
            share_value = None
            if update.message.text is not None and update.message.text.startswith('/start exam_'):
                share_value = update.message.text.replace("/start exam_", "")

            if user_data is None:
                username = update.message.from_user.username
                is_premium = update.message.from_user.is_premium
                print(111)
                print("username:", username)
                print("is_premium:", is_premium)
                print("share_value:", share_value)
                user_data = await f_user.create_user(user_id, username, is_premium, share_value)
                print(222)
                try:
                    await bot.send_message(
                        ADMINS[0],
                        const_text('admin_new_user_to_channel').format(
                            user_id=user_id,
                            fullname=update.message.from_user.full_name.replace("<", "").replace(">", ""),
                            username=username,
                            is_premium="✅ Premium obunachi" if is_premium else "Oddiy obunachi",
                            created_at=str(toshkent_now()).split(".", 1)[0]
                        )
                    )
                except:
                    pass
            fullname = user_data.fullname
            region = user_data.region
            district = user_data.district
            phone = user_data.phone
            referral_count = user_data.referral_count
            if referral_count is None:
                await f_user.update_user(user_id, referral_count=referral_count)

            lang = await f_user.select_user_language(user_id)
            if lang is None:
                await update.message.answer(const_text("user_register_language"), reply_markup=language_picker)
                raise CancelHandler()
            if update.message.text == '/start' and fullname is None:
                await update.message.answer("Iltimos, ismingiz va familiyangizni kiriting:")
                raise CancelHandler()
            if fullname is None:
                await f_user.update_user(user_id, fullname=update.message.text)
                if region is not None:
                    await user_settings_handler(update.message)
                    return
                await update.message.answer(text("user_register_region", lang), reply_markup=region_picker(lang))
                raise CancelHandler()
            if region is None:
                await update.message.answer(text("user_register_region", lang), reply_markup=region_picker(lang))
                raise CancelHandler()
            if district is None:
                await update.message.answer(text("user_register_district", lang),
                                            reply_markup=district_picker(region, lang))
                raise CancelHandler()
            if update.message.contact is None and phone is None:
                await send_phone_request(user_id)
                raise CancelHandler()

        if update.callback_query and not update.callback_query.data.startswith(("district:", 'region:')):
            lang = await f_user.select_user_language(user_id)
            if lang:
                status, keyboard = await check_status(user_id, lang)
                if not status:
                    try:
                        await update.callback_query.message.edit_text(
                            text("user_subscribe_request", lang),
                            reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard),
                            disable_web_page_preview=True
                        )
                    except:
                        try:
                            await update.callback_query.answer("⚠️ Kanalga a'zo bo'ling", cache_time=0)
                        except:
                            pass

                    raise CancelHandler()
            else:
                if update.callback_query.data.startswith('lang:'):
                    return

                await update.callback_query.message.answer(const_text("user_register_language"),
                                                           reply_markup=language_picker)
                raise CancelHandler()
