import os
import shutil
import subprocess
import json
import base64
import requests
from io import BytesIO
from PIL import Image
from bs4 import BeautifulSoup
from docx import Document
from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.types import ContentType

from keyboards.inline.inline_admin import get_diagnostika_list_buttons, admin_back_menu
from loader import dp
from states.admin import UploadTestState
from utils.database.functions.f_diagnostika import link_subject_to_diagnostika
from utils.database.functions.f_questions import create_question
from utils.database.functions.f_answers import create_answer

IMGBB_API_KEY = "84d34ba6c27b025e68c06165726c4bf1"
SUPPORTED_FORMATS = {"JPEG", "PNG", "GIF", "BMP", "TIFF"}

def check_pandoc_installed():
    return shutil.which("pandoc") is not None

def convert_docx_to_html(docx_path):
    if not check_pandoc_installed():
        raise RuntimeError("❌ Pandoc o'rnatilmagan! Iltimos, Pandoc'ni o‘rnating.")
    html_path = docx_path.replace(".docx", ".html")
    try:
        subprocess.run(
            ["pandoc", docx_path, "-o", html_path, "--from=docx", "--to=html+tex_math_dollars", "--mathjax"],
            check=True
        )
        return html_path
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"❌ Pandoc orqali konvertatsiyada xatolik yuz berdi: {e}")

def convert_to_latex(text):
    return f"{text}"
def convert_image_to_supported_format(image_blob):
    try:
        image = Image.open(BytesIO(image_blob))
        if image.format not in SUPPORTED_FORMATS:
            img_io = BytesIO()
            image.convert("RGB").save(img_io, format="PNG")
            return img_io.getvalue()
        return image_blob
    except Exception as e:
        print(f"❌ Rasmni konvertatsiya qilishda xatolik: {e}")
        return None
def upload_image_to_imgbb(image_blob):
    url = "https://api.imgbb.com/1/upload"
    image_blob = convert_image_to_supported_format(image_blob)
    if image_blob is None:
        print("❌ Rasmni PNG formatiga o'tkazishda xatolik!")
        return None
    try:
        encoded_image = base64.b64encode(image_blob).decode("utf-8")
        payload = {"key": IMGBB_API_KEY, "image": encoded_image}
        response = requests.post(url, data=payload)

        if response.status_code == 200:
            return response.json()["data"]["url"]
        else:
            print(f"❌ ImgBB yuklashda xatolik! Status Code: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Rasmni yuklashda xatolik: {e}")
        return None


@dp.callback_query_handler(
    lambda call: call.data.startswith("admin_add_test:") or call.data.startswith("admin_add_mandatory_test:"),
    state="*")
async def ask_for_doc(call: types.CallbackQuery, state: FSMContext):
    data_parts = call.data.split(":")
    if len(data_parts) < 3:
        await call.answer("❌ Xatolik: Diagnostika yoki fan ID topilmadi!", show_alert=True)
        return

    subject_id = int(data_parts[1])
    diagnostika_id = int(data_parts[2])
    is_mandatory = call.data.startswith("admin_add_mandatory_test")

    await state.update_data(subject_id=subject_id, diagnostika_id=diagnostika_id, is_mandatory=is_mandatory)

    test_type = "Majburiy" if is_mandatory else "Oddiy"
    await call.message.edit_text(f"📄 Iltimos, <b>{test_type}</b> test uchun DOCX fayl yuklang!", reply_markup=admin_back_menu)
    await UploadTestState.waiting_for_docx.set()


@dp.message_handler(content_types=ContentType.DOCUMENT, state=UploadTestState.waiting_for_docx)
async def handle_docx(message: types.Message, state: FSMContext):
    document = message.document
    await message.answer("⏳")
    if not document.file_name.endswith(".docx"):
        await message.answer("❌ Faqat DOCX formatdagi fayl yuklang!")
        return

    os.makedirs("downloads", exist_ok=True)
    file_path = f"downloads/{document.file_name}"
    await document.download(destination_file=file_path)

    subject_data = await state.get_data()
    subject_id = subject_data.get("subject_id")
    diagnostika_id = subject_data.get("diagnostika_id")
    is_mandatory = subject_data.get("is_mandatory", False)

    required_question_count = 10 if is_mandatory else 30
    questions = await extract_questions_from_docx(file_path)

    total_questions = len(questions)
    if total_questions != required_question_count:
        difference = required_question_count - total_questions
        if difference > 0:
            await message.answer(f"⚠️ Xatolik: {total_questions} ta savol bor. {difference} ta savol yetishmayapti!")
        else:
            await message.answer(f"⚠️ Xatolik: {total_questions} ta savol bor. {abs(difference)} ta ortiqcha!")
        os.remove(file_path)
        await state.finish()
        return
    await process_docx(file_path, message, subject_id, diagnostika_id, questions, is_mandatory)
    os.remove(file_path)


async def extract_questions_from_docx(file_path):
    try:
        html_path = convert_docx_to_html(file_path)
    except RuntimeError as e:
        print(str(e))
        return []

    with open(html_path, "r", encoding="utf-8") as file:
        soup = BeautifulSoup(file, "html.parser")

    document = Document(file_path)
    paragraphs = soup.find_all(["p", "img"])
    questions = []
    current_question = None
    options = []
    correct_answer_found = False
    question_text = ""
    current_image_url = None
    for element in paragraphs:
        if element.name == "img":
            img_rel_id = element.get("src")
            if img_rel_id:
                try:
                    for rel in document.part.rels.values():
                        if img_rel_id in rel.target_ref:
                            image_blob = rel.target_part.blob
                            current_image_url = upload_image_to_imgbb(image_blob)
                            print(f"✅ ImgBB: Yuklangan URL: {current_image_url}")
                            break
                except Exception as e:
                    print(f"❌ Rasmni yuklashda xatolik: {e}")
            continue

        text = element.get_text(strip=False)

        if text.startswith("@&"):
            if current_question:
                if len(options) == 4 and correct_answer_found:
                    questions.append({
                        "question": convert_to_latex(question_text.strip()),
                        "options": [(convert_to_latex(opt[0]), opt[1]) for opt in options],
                        "image": current_image_url
                    })
                else:
                    print(f"❌ Xatolik: {question_text} savolida 4 ta variant yoki to‘g‘ri javob mavjud emas!")

            current_question = text.replace("@&", "").strip()
            question_text = current_question
            options = []
            correct_answer_found = False
            current_image_url = None

        elif text.startswith("@#") or text.startswith("@"):
            is_correct = text.startswith("@#")
            option_text = text.replace("@#", "").replace("@", "").strip()
            if is_correct:
                correct_answer_found = True
            options.append((option_text, is_correct))

        else:
            question_text += f" {text}"

    if current_question and len(options) == 4 and correct_answer_found:
        questions.append({
            "question": convert_to_latex(question_text.strip()),
            "options": [(convert_to_latex(opt[0]), opt[1]) for opt in options],
            "image": current_image_url
        })

    os.remove(html_path)
    return questions

async def process_docx(file_path, message, subject_id, diagnostika_id, questions, is_mandatory):
    for q in questions:
        question_obj = await create_question(
            subject_id=subject_id,
            diagnostika_id=diagnostika_id,
            question_text=q["question"],
            image=q["image"],
            is_mandatory=is_mandatory
        )
        for text, is_correct in q["options"]:
            await create_answer(text=text, is_correct=is_correct, question_id=question_obj.id)

    await link_subject_to_diagnostika(subject_id, diagnostika_id)

    test_type = "Majburiy" if is_mandatory else "Oddiy"
    text, keyboard = await get_diagnostika_list_buttons(subject_id)
    await message.answer(f"✅ <b>{test_type}</b> testlar muvaffaqiyatli qo‘shildi! ({len(questions)} ta)\n\n{text}", reply_markup=keyboard)
