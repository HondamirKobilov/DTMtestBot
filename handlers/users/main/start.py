from typing import Union
from aiogram import types
from aiogram.dispatcher import FSMContext
from data.config import VARIANTS_CHANNEL
from data.texts import text, buttons
from keyboards.default.default_user import *
from keyboards.inline.inline_blok import result_inline_button
from keyboards.inline.inline_user import kb_variant_answer, inline_keyboard_markup
from loader import dp, bot
from states.user import Dispatch
from utils.database.functions import f_user

@dp.message_handler(commands=['start'], state="*", run_task=True)
@dp.message_handler(text=buttons("user_back"), state="*", run_task=True)
async def user_start_handler(message: Union[types.Message, types.CallbackQuery], state: FSMContext):
    user_id = message.from_user.id
    lang = await f_user.select_user_language(user_id)
    if isinstance(message, types.Message):
        if message.text.startswith('/start check_blok_'):
            check_blok = message.text.replace("/start check_blok_", "")
            check_blocks = check_blok.split("_")

            captions = []
            media = []
            fan_names = []
            variant_ids = []

            # Bloklarni qayta ishlash
            print("Blok ma'lumotlarini tahlil qilamiz:")
            for idx, check_block in enumerate(check_blocks, start=1):
                if check_block == "0-0":
                    variant_ids.append(int(0))
                    print(f"{idx}-Blok: Kasbiy (ijodiy) imtihon")
                    fan_names.append("Kasbiy (ijodiy) imtihon")
                    captions.append(
                        f"{idx}-Blok\n"
                        f"📚 Fan nomi: Kasbiy (ijodiy) imtihon\n"
                        f"📈 Test savollari soni: Ma'lumot yo'q"
                    )
                    continue
                elif "-" in check_block and len(check_block.split("-")) == 2:
                    fan_id, variant_id = check_block.split("-")
                    print(f"{idx}-Blok: Fan ID - {fan_id}, Variant ID - {variant_id}")


                    subject_name = await get_subject_name_by_variant_id(int(variant_id))
                    if not subject_name:
                        await message.answer(f"❌ {idx}-Blok uchun fan nomi topilmadi.")
                        return

                    variant = await f_subject.get_variant_by_id(int(variant_id))
                    if not variant:
                        await message.answer(f"❌ {idx}-Blok uchun variant topilmadi.")
                        return

                    fan_names.append(subject_name)

                    variant_ids.append(int(variant_id))

                    # Media va caption qo'shish
                    media.append(types.InputMediaDocument(media=variant.file_id))
                    captions.append(
                        f"{idx}-Blok\n"
                        f"📚 Fan nomi: {subject_name}\n"
                        f"📈 Test savollari soni: 30"
                    )
                else:
                    # Xato formatni aniqlash
                    await message.answer(f"❌ {idx}-Blok ma'lumotlari noto'g'ri formatda.")
                    return

            # Fan nomlari va variant ID'larni statega yozish
            await state.update_data(fan_names=fan_names, variant_ids=variant_ids)

            # Javob matni tayyorlash
            additional_text = (
                "Marhamat o'z javoblaringizni yuboring\n"
                "Javoblarni quyidagi namunadek yuboring:\n\n"
                "abcdaBacAac..."
            )

            await Dispatch.user_block_answer.set()

            # Media yuborish
            if media:
                await bot.send_media_group(chat_id=message.chat.id, media=media)

            # Yakuniy matnni yuborish
            await message.answer("\n\n".join(captions) + "\n\n" + additional_text)
            return

        # `/start exam_` bo'lsa
        if message.text.startswith('/start exam_'):
            variant_id = message.text.replace("/start exam_", "")
            await Dispatch.user_waiting_for_variant_answer.set()
            await make_variant(user_id, state, lang, variant_id)
            return

        await message.answer(text("user_start", lang), reply_markup=kb_main_menu(lang))

    elif isinstance(message, types.CallbackQuery):
        await message.message.answer(text("user_start", lang), reply_markup=kb_main_menu(lang))


@dp.message_handler(state=Dispatch.user_block_answer)
async def handle_user_answers(message: types.Message, state: FSMContext):
    user_answers = message.text.strip().upper()  # Javoblarni katta harfga o'tkazish
    max_answers = 90  # Maksimal javoblar soni
    questions_per_column = 30  # Har bir ustunda 30 ta savol
    await state.update_data(user_answers=user_answers)

    data = await state.get_data()
    fan_names = data.get("fan_names", [])

    kasbiy_indexes = [
        i for i, name in enumerate(fan_names)
        if name in ["Kasbiy (ijodiy) imtihon", "Профессиональный (творческий) экзамен"]
    ]

    remaining_answers = list(user_answers) + ["❓"] * (max_answers - len(user_answers))
    allocated_answers = []

    for idx in range(3):
        if idx in kasbiy_indexes:
            allocated_answers.append([""] * questions_per_column)
        else:
            allocated_answers.append(remaining_answers[:questions_per_column])
            remaining_answers = remaining_answers[questions_per_column:]

    result_text = "<b>Test javoblaringiz:</b>\n\n"

    sorted_answers = [""] * max_answers  # Bo'sh list yaratamiz, uzunligi 90
    for i in range(questions_per_column):
        for col_idx in range(3):
            index = i + col_idx * questions_per_column  # Global tartib raqam
            answer = allocated_answers[col_idx][i] if i < len(allocated_answers[col_idx]) else ""
            if answer and answer != "❓":
                sorted_answers[index] = answer  # Javobni o'z tartib raqamiga joylash

    # "Kasbiy (ijodiy) imtihon" bo'limi haqida xabar
    for idx in kasbiy_indexes:
        if idx < len(fan_names):
            result_text += f"❕ {fan_names[idx]} uchun savollar mavjud emas. Ushbu bo'lim ochiq qoldirildi.\n\n"

    # Javoblarni formatlash
    for i in range(questions_per_column):
        row = ""
        for col_idx in range(3):  # Uch ustun
            index = i + col_idx * questions_per_column
            answer = allocated_answers[col_idx][i] if i < len(allocated_answers[col_idx]) else "❓"
            row += f"{index + 1:02d}. {answer:<3}    " if answer else f"{index + 1:02d}.        "

        # Ustunlarni moslashtirish uchun bo'shliqlar
        row = row.ljust(50)
        result_text += row.rstrip() + "\n"

        # Har 30 savoldan keyin fan nomini qo‘shish
        if (i + 1) % 30 == 0:
            fan_index = (i // 30)
            if fan_index < len(fan_names):
                subject_name = fan_names[fan_index]
                if subject_name not in ["Kasbiy (ijodiy) imtihon", "Профессиональный (творческий) экзамен"]:
                    result_text += f"\n➡️ {subject_name} javoblari tugadi. Keyingi bo‘lim:\n\n"

    await state.update_data(sorted_answers=sorted_answers)
    await message.answer(result_text, reply_markup=inline_keyboard_markup())

    # Tartiblangan javoblarni chop etish
    print("Tartiblangan javoblar:", sorted_answers)


@dp.callback_query_handler(lambda call: call.data == "resend_answers", state="*")
async def resend_answers_handler(call: types.CallbackQuery, state: FSMContext):
    await call.message.edit_text(
        "Iltimos, javoblaringizni qayta kiriting:\n\n"
        "abcdaBacAac... mana shu ko'rinishda bo'lishi kerak."
    )
    await Dispatch.user_block_answer.set()
    await call.answer()

@dp.callback_query_handler(lambda call: call.data == "confirm_answers", state="*")
async def confirm_answers_handler(call: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    variant_ids = data.get("variant_ids", [])
    sorted_answers = data.get("sorted_answers", [])
    fan_names = data.get("fan_names", [])

    correct_answers_list = []

    # To'g'ri javoblarni yig'ish
    for variant_id in variant_ids:
        if variant_id == 0:
            correct_answers_list.extend([""] * 30)  # Kasbiy fan uchun bo'sh joy
        else:
            correct_answer = await get_answer_key_by_variant_id(variant_id)
            if correct_answer:
                correct_answers_list.extend(list(correct_answer))

    # Ballar hisoblash uchun
    section_scores = [0, 0, 0]  # 3 bo'lim uchun ballar
    total_correct = 0
    total_wrong = 0

    # Javoblarni chiqarish uchun matn tayyorlash
    result_text = "<b>📝 Test javoblaringiz:</b>\n\n"

    # "Kasbiy (ijodiy) imtihon" xabarini qo'shish
    for idx, name in enumerate(fan_names):
        if name in ["Kasbiy (ijodiy) imtihon", "Профессиональный (творческий) экзамен"]:
            result_text += f"❕ <b>{name}</b> uchun savollar mavjud emas. Ushbu bo'lim ochiq qoldirildi.\n\n"

    # Javoblarni formatlash va solishtirish
    for i in range(30):  # Har bir ustunda 30 satr
        row = ""
        for col_idx in range(3):  # Uchta ustun
            index = i + col_idx * 30
            user_answer = sorted_answers[index] if index < len(sorted_answers) else "❓"
            correct_answer = correct_answers_list[index] if index < len(correct_answers_list) else ""

            # To'g'ri yoki noto'g'riligini aniqlash
            if user_answer == "❓" or user_answer == "":
                answer_display = "❓"
                section_scores[col_idx] += 0  # Bo'sh yoki noto'g'ri bo'lsa 0 ball
            elif user_answer == correct_answer:
                answer_display = f"{user_answer} ✅"
                section_scores[col_idx] += 3.1 if col_idx == 0 else 2.1 if col_idx == 1 else 1.1
                total_correct += 1
            else:
                answer_display = f"{user_answer} ❌ ({correct_answer})"
                section_scores[col_idx] += 0  # Noto'g'ri bo'lsa 0 ball
                total_wrong += 1

            # Har bir ustun orasidagi joylashuv
            row += f"{index + 1:02d}. {answer_display:<20}"
        result_text += row.rstrip() + "\n"

    # Jami ball va natijalarni qo'shish
    jami_ball = sum(section_scores)
    result_text += "\n<b>📊 Natijalar:</b>\n"
    result_text += f"1-Fan (3.1 ball har to‘g‘ri javob): <b>{section_scores[0]:.1f} ball</b>\n"
    result_text += f"2-Fan (2.1 ball har to‘g‘ri javob): <b>{section_scores[1]:.1f} ball</b>\n"
    result_text += f"3-Majburiy fanlar (1.1 ball har to‘g‘ri javob): <b>{section_scores[2]:.1f} ball</b>\n"
    result_text += f"Jami ball: <b>{jami_ball:.1f}</b>\n"
    result_text += f"To'g'ri javoblar soni: <b>{total_correct}</b>\n"
    result_text += f"Noto'g'ri javoblar soni: <b>{total_wrong}</b>\n"

    # Qo'shimcha xabar
    result_text += (
        "\n<b>❗️ Siz to'plagan balingiz orqali yo'nalishingiz bo'yicha kontrakt yoki grant talabasi "
        "bo'lishingizni bilib oling:</b>\n"
    )

    # Inline tugmani qo'shish
    await call.message.edit_text(result_text, reply_markup=result_inline_button(jami_ball), parse_mode="HTML")

    # Debug uchun chiqarish
    print("Variant IDs:", variant_ids)
    print("Correct Answers:", correct_answers_list)
    print("Sorted Answers:", sorted_answers)
    print("Section Scores:", section_scores)
    print("Total Correct:", total_correct)
    print("Total Wrong:", total_wrong)




