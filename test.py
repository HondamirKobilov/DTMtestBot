import os
import fitz  # PyMuPDF
from PyPDF2 import PdfMerger
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import InputFile
from aiogram.utils import executor

API_TOKEN = '7939786322:AAFlUcOh9lvy5tAvAEe_aJgEKbzTMKX4cLg'  # Bot tokeningizni kiriting

bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)


class UploadPDF(StatesGroup):
    first_pdf = State()
    second_pdf = State()


@dp.message_handler(commands='start')
async def cmd_start(message: types.Message):
    await message.answer("Iltimos, birinchi PDF faylni yuboring.")
    await UploadPDF.first_pdf.set()


@dp.message_handler(content_types=['document'], state=UploadPDF.first_pdf)
async def handle_first_pdf(message: types.Message, state: FSMContext):
    document = message.document
    file_path = await save_file(document)
    await state.update_data(first_pdf=file_path)
    await message.answer("Endi ikkinchi PDF faylni yuboring.")
    await UploadPDF.second_pdf.set()


@dp.message_handler(content_types=['document'], state=UploadPDF.second_pdf)
async def handle_second_pdf(message: types.Message, state: FSMContext):
    document = message.document
    file_path = await save_file(document)
    await state.update_data(second_pdf=file_path)

    data = await state.get_data()

    merged_pdf_path = "merged_output.pdf"
    merge_pdfs(data['first_pdf'], data['second_pdf'], merged_pdf_path)

    numbered_pdf_path = "numbered_output.pdf"
    update_question_numbers(merged_pdf_path, numbered_pdf_path)

    if os.path.exists(numbered_pdf_path):
        await message.answer("Yangi PDF tayyor! Faylni yuklayapman.")
        await message.answer_document(InputFile(numbered_pdf_path))
    else:
        await message.answer("Xatolik yuz berdi, PDF fayl yaratilgani yo'q.")

    # Fayllarni o'chirish
    os.remove(data['first_pdf'])
    os.remove(data['second_pdf'])
    os.remove(merged_pdf_path)
    os.remove(numbered_pdf_path)
    await state.finish()


async def save_file(document: types.Document):
    file = await bot.download_file_by_id(document.file_id)
    file_path = f"{document.file_name}"

    with open(file_path, 'wb') as f:
        f.write(file.read())

    return file_path


def merge_pdfs(first_pdf, second_pdf, output_pdf):
    merger = PdfMerger()
    merger.append(first_pdf)
    merger.append(second_pdf)
    merger.write(output_pdf)
    merger.close()


# Tartib raqam ekanini aniqlash funksiyasi
def is_question_number(line_text):
    # Raqam va "." bilan boshlangan satrlarni tanlab olamiz
    if line_text and line_text[0].isdigit():
        dot_pos = line_text.find(".")
        if dot_pos != -1 and line_text[:dot_pos].isdigit():
            return True
    return False


def update_question_numbers(input_pdf, output_pdf):
    doc = fitz.open(input_pdf)
    question_count = 1

    for page_num in range(len(doc)):
        page = doc[page_num]
        text_instances = page.get_text("dict")

        for block in text_instances["blocks"]:
            if "lines" in block:
                for line in block["lines"]:
                    for span in line["spans"]:
                        line_text = span["text"].strip()

                        # Faqat tartib raqam ekanini aniqlab, yangilaymiz
                        if is_question_number(line_text):
                            dot_pos = line_text.find(".")
                            if dot_pos != -1:
                                old_question_num = line_text[:dot_pos + 1]
                                new_question_text = f"{question_count}."

                                # Tartib raqam joylashgan hududni faqat oq rang bilan qoplash
                                rect = fitz.Rect(span["bbox"][0], span["bbox"][1], span["bbox"][0] + 13, span["bbox"][3])
                                page.draw_rect(rect, color=(1, 1, 1), fill=(1, 1, 1))  # Oq rang bilan qoplash
                                bold_font_path = "Arial-Bold.ttf"
                                # Faqat yangi tartib raqamni yozish, qolgan matn o'zgarmaydi
                                page.insert_text((span["bbox"][0], span["bbox"][1]+10), new_question_text,
                                                 fontsize=span["size"], color=(0, 0, 0), fontfile=bold_font_path, overlay=True)  # Yangi raqam yozish
                                question_count += 1

    # Yangi tahrirlangan PDFni saqlash
    doc.save(output_pdf)
    doc.close()


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)