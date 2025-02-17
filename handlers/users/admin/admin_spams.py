import asyncio

from aiogram import types
from aiogram.dispatcher import FSMContext

from data.texts import const_text
from filters import F
from keyboards.inline.inline_admin import admin_back_menu
from loader import bot, dp
from utils.database.functions import f_user


async def post_message_to_user(user, message: types.Message, reply_markup):
    user_id, fullname = user
    try:
        if message.html_text is not None:
            message_text = message.html_text.format(fullname=fullname)
            if message.text is not None:
                await bot.send_message(user_id, message_text, reply_markup=reply_markup)
            else:
                if message.content_type == 'document':
                    await bot.send_document(user_id, document=message.document.file_id, caption=message_text,
                                            reply_markup=reply_markup)
                elif message.content_type == 'photo':
                    await bot.send_photo(user_id, photo=message.photo[-1].file_id, caption=message_text,
                                         reply_markup=reply_markup)
                elif message.content_type == 'video':
                    await bot.send_video(user_id, video=message.video.file_id, caption=message_text,
                                         reply_markup=reply_markup)
                elif message.content_type == 'audio':
                    await bot.send_audio(user_id, audio=message.audio.file_id, caption=message_text,
                                         reply_markup=reply_markup)
                elif message.content_type == 'voice':
                    await bot.send_voice(user_id, voice=message.voice.file_id, caption=message_text,
                                         reply_markup=reply_markup)
                elif message.content_type == 'animation':
                    await bot.send_animation(user_id, animation=message.animation.file_id, caption=message_text,
                                             reply_markup=reply_markup)
        else:
            await message.copy_to(user_id, reply_markup=reply_markup)
        print("✅✅✅", user_id, "ga yuborildi")
        return 1, 0
    except Exception as e:
        return await handle_post_error(user, message, reply_markup, e)


async def handle_post_error(user, message, reply_markup, exception):
    user_id, fullname = user
    error_message = str(exception)
    if "blocked" in error_message or "deactivated" in error_message or "not found" in error_message:
        print("❌❌❌", user_id, "------ ga bormadi!!!! \n", str(exception))
        await f_user.update_user(user_id, is_blocked=True)
        return 0, 1

    if "Flood control" in error_message:
        sleep_time = int(error_message.split()[-2])
        print("💤💤💤 ", sleep_time, " sekundga pauza bo'ldi\n", str(exception))
        await asyncio.sleep(sleep_time)
        return await post_message_to_user(user, message, reply_markup)
    print("⭕️⭕️⭕️⭕️", user_id, "\n", str(exception))
    return 0, 0


async def process_user_group(users, message, reply_markup):
    count_sent, count_blocked = 0, 0
    for user in users:
        sent, blocked = await post_message_to_user(user, message, reply_markup)
        # await asyncio.sleep(0.7)
        count_sent += sent
        count_blocked += blocked
    return count_sent, count_blocked


async def distribute_message(users, message, reply_markup, group_size=40, delay=1):
    total_users = len(users)
    count = total_users // group_size
    if count == 0:
        count = 1
    last_group_size = total_users % count

    tasks = []
    for i in range(group_size):
        start_index = i * count
        end_index = start_index + count
        tasks.append(asyncio.create_task(
            process_user_group(users[start_index:end_index], message, reply_markup)
        ))
        await asyncio.sleep(delay)

    if last_group_size > 0:
        tasks.append(asyncio.create_task(
            process_user_group(users[-last_group_size:], message, reply_markup)
        ))

    results = await asyncio.gather(*tasks)
    return sum(r[0] for r in results), sum(r[1] for r in results)


@dp.message_handler(F.AdminFilter(), commands=['post', 'send'], state="*", run_task=True)
async def message_post(message: types.Message, state: FSMContext):
    if message.reply_to_message:
        try:
            await bot.send_message(message.from_user.id, const_text("admin_started_sending_messages"))
            print(const_text("admin_started_sending_messages"))
            post_type = message.text.replace("post", "").replace("send", "")
            users = await f_user.get_all_users_posts(post_type and "not" in post_type)
            reply_markup = message.reply_to_message.reply_markup
            total_sent, total_blocked = await distribute_message(users, message.reply_to_message, reply_markup)
            await message.answer(const_text("admin_message_distribution_completed").format(total_sent=total_sent,
                                                                                                 total_blocked=total_blocked))
        except Exception as ex:
            print("send qilyatganda:", ex)
    else:
        await bot.send_message(message.from_user.id, const_text("admin_reply_to_post_command"))


@dp.callback_query_handler(F.AdminFilter(), text='admin_send_message', state="*", run_task=True)
async def message_send_handler(call: types.CallbackQuery, state: FSMContext):
    await call.message.edit_text(const_text("admin_send_message_instruction"), reply_markup=admin_back_menu)
