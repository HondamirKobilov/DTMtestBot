from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.callback_data import CallbackData

subject_cb = CallbackData("s", "subject_id", "action")

def generate_subject_keyboard(subjects):
    markup = InlineKeyboardMarkup(row_width=2)
    for subject in subjects:
        markup.insert(InlineKeyboardButton(subject.name, callback_data=subject_cb.new(subject_id=subject.id, action="do")))
        markup.insert(InlineKeyboardButton("  ", callback_data=subject_cb.new(subject_id=0, action="nothing")))

    return markup

def generate_related_subject_keyboard(selected_subject, subjects, related_subjects, selected_related_subject=None):
    markup = InlineKeyboardMarkup(row_width=2)

    for i, subject in enumerate(subjects):
        text = f"✅ {subject.name}" if subject.name.lower() == selected_subject.lower() else subject.name
        markup.insert(InlineKeyboardButton(text, callback_data=subject_cb.new(subject_id=subject.id, action="do")))

        if i < len(related_subjects):
            related = related_subjects[i]
            text = f"✅ {related.name}" if selected_related_subject and selected_related_subject.name.lower() == related.name.lower() else related.name
            markup.insert(
                    InlineKeyboardButton(text, callback_data=subject_cb.new(subject_id=related.id, action='do-related')))

        else:
            markup.insert(InlineKeyboardButton("  ", callback_data=subject_cb.new(subject_id=0, action="nothing")))

    if selected_related_subject is not None:
        markup.add(
            InlineKeyboardButton("📝 Testni boshlash", callback_data="confirm_selection")
        )

    return markup

def generate_check_button(referral_link: str):

    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton(text="🔎 Javobni tekshirish", url=referral_link))
    return keyboard

def result_inline_button(jami_ball: float):
    button_url = f"https://t.me/DTMStat_bot?start={float(jami_ball)}"
    keyboard = InlineKeyboardMarkup(row_width=1)
    keyboard.add(
        InlineKeyboardButton("Natija 📊", url=button_url)
    )
    return keyboard