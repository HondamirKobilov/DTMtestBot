_const_texts = {
    "admin_new_user_to_channel": """<b>🆕 Yangi foydalanuvchi:</b>
<b>Ismi:</b> 👉 <a href='tg://user?id={user_id}'>{fullname}</a>
<b>ID:</b> {user_id}
<b>Username:</b> @{username}

{is_premium}

{created_at}""",
    "admin_start": """⚡️ Assalomu alaykum, Hurmatli {fullname}
<a href=\"https://telegra.ph/file/aa08d65c33a2664e1abe8.jpg\"> </a>
Marhamat siz uchun admin paneli quyidagilar""",
    "admin_statistics": """📊┌ STATISTIKA
👥├ A`zolar: {all_users} ta
👥├ Faol a'zolar: {active_users} ta
👥├ Bugun kirganlar: {today_users} ta
👥├ Premium obunachilar: {premium_users} ta""",
    "admin_started_sending_messages": "<b>Xabar tarqatish boshlandi!</b>",
    "admin_message_distribution_completed": """<b>Xabarni tarqatish tugallandi.</b>

<b>Jami yuborilgan xabarlar:</b> <code>{total_sent}</code>
<b>Jami bloklangan foydalanuvchilar:</b> <code>{total_blocked}</code>""",
    "admin_reply_to_send_command": """<b>Biror bir xabarga reply qilib yozing
(<code>/send</code>)</b>""",
    "admin_send_message_instruction": """<a href='telegra.ph/file/31c6e3fd53055c1388dac.jpg'> </a>Istalgan xabarni forward yoki oddiy yuboring va yuborgan xabaringizga <b><u>reply</u></b> qilib,
<code>/send</code> buyrug'ini yuboring!
Batafsil quyida:""",
    "admin_channel_added": """✅ <b>Kanal qo'shildi: 
{channel_name}</b> (ID: {channel_id})""",
    "admin_manage_channels_intro": "<b>💠 Kanallar boshqaruvi:</b>",
    "admin_enter_new_channel_id": "<b>Iltimos, yangi kanalning IDsini kiriting:</b>",
    "admin_enter_channel_name": "<b>Endi kanal nomini kiriting:</b>",
    "admin_channel_not_found": "🚫 Kanal topilmadi.",
    "admin_channel_edit_prompt": """<b>📢 Kanal: {channel_title}</b>
Nima qilmoqchisiz?""",
    "admin_channel_deleted": "🗑 Kanal o'chirildi.",
    "admin_enter_new_channel_id_for_modification": "<b>Iltimos, kanalning yangi ID'sini kiriting:</b>",
    "admin_enter_new_channel_name": "<b>Endi yangi kanal nomini kiriting:</b>",
    "admin_channel_modified": """<b>🔄 Kanal yangilandi:</b>
 {new_channel_name} (ID: {new_channel_id})
Nima qilmoqchisiz?""",
    "admin_subject_added": """✅ <b>Fan qo'shildi: 
{subject_name}</b> (ID: {subject_id})

{subject_lang}""",
    "admin_manage_subjects_intro": "<b>🔸 Fanlar ro'yxati:</b>",
    "admin_enter_new_subject_name": "<b>Iltimos, yangi fanni nomini kiriting:</b>",
    "admin_subject_not_found": "🚫 Fan topilmadi.",
    "admin_variant_not_found": "🚫 Variant topilmadi.",
    "admin_subject_edit_prompt": """<b>Test fani:</b> {subject_name}
<b>Test tili:</b> <code>{subject_language}</code>
<b>Javoblar:</b> <code>{subject_answer_key}</code>
<b>Test fayli:</b> <b>{subject_document}</b>

🔗 Kanal linki: https://t.me/+j24WXPX-rpFhYTIy

O'chirmoqchimisiz?""",
    "admin_subject_deleted": "🗑 Fan o'chirildi.",
    "admin_variant_deleted": "🗑 Variant o'chirildi.",
    "admin_enter_new_variant_answer_key": "<b>Iltimos, Variantni javoblarini kiriting: (ABCD...)</b>",
    "admin_enter_new_variant_document": "<b>Iltimos, Variantni PDF faylini yuboring:</b>",
    "user_register_language": "🇺🇿 O'zingizga kerakli tilni tanlang:"
                              "\n\n🇷🇺 Выберите язык, который вы хотите:",
}

_const_buttons = {
    "admin_diaginostika": "🔸 Diaginostika",
    "admin_subjects": "📄 Fanlar ro'yxati",
    "admin_send_message": "📤 Xabar yuborish",
    "admin_statistics": "👤 Foydalanuvchilar soni",
    "admin_manage_channels": "⚙️ Kanallar boshqaruvi",
    "admin_add_channel": "🆕 Yangi kanal qo'shish",
    "admin_add_subject": "🆕 Yangi fan qo'shish",
    "admin_ref": "🔗 Referal",
    "admin_group": "👥 Group",
    "admin_home": "🏠 Bosh menyu",
    "admin_back": "🔙 Ortga",
    "admin_delete": "❌ O'chirish",
    "admin_edit": "✏️ Tahrirlash"
}

lang_button = {
    "uz": "🇺🇿 O'zbek",
    "ru": "🇷🇺 Русский",
    "kr": "🇺🇿 Qoraqalpoq",
}


def const_text(key):
    return _const_texts[key]


def const_button(key):
    return _const_buttons[key]


_translated_texts = {
    "select_second_subject": {
        "uz": "2-Fan (mutaxassislik)ni tanlang:",
        "ru": "Выберите второй предмет (специализация):"
    },
    "user_start": {
        "uz": "Assalomu alaykum, bot orqali doimiy tarzda testlar ishlab borishingiz mumkin!",
        "ru": "Здравствуйте, вы можете регулярно работать над тестами с помощью бота!"
    },
    "user_select_language": {
        "uz": "Test tilini tanlang",
        "ru": "Выберите язык теста"
    },
    "user_select_subject": {
        "uz": "Fanni ko’rsating:",
        "ru": "Укажите предмет:"
    },
    "user_select_variant": {
        "uz": "Variantni ko’rsating:",
        "ru": "Укажите вариант:"
    },
    "user_register_name": {
        "uz": "Ism va familiyangizni kiriting:",
        "ru": "Введите ваше имя и фамилию:"
    },
    "user_register_region": {
        "uz": "Viloyatingizni tanlang:",
        "ru": "Выберите ваш регион:"
    },
    "user_register_district": {
        "uz": "Tumaningizni tanlang:",
        "ru": "Выберите ваш район:"
    },
    "user_register_phone": {
        "uz": "Telefon raqamingizni '{user_phone_number}' tugmasini bosgan holda yuboring:",
        "ru": "Отправьте свой номер телефона, нажав «{user_phone_number}»:"
    },
    "user_subscribe_request": {
        "uz": "Botni ishlatish uchun quyidagi kanalga obuna bo'lish talab qilinadi!",
        "ru": "Для использования бота требуется подписка на следующий канал!"
    },
    "user_please_wait": {
        "uz": "Iltimos biroz kutib turing...",
        "ru": "Пожалуйста, подождите немного..."
    },
    "user_settings": {
        "uz": """To'liq ism: {fullname}
Telefon raqam: {phone}
Viloyat: {region}
Tuman/shahar: {district}

🇺🇿""",
        "ru": """Имя: {fullname}
Телефон: {phone}
Oбласть: {region}
Pайон/город: {district}

🇷🇺"""
    },
    "user_invalid_answer": {
        "uz": """Iltimos kalitlarni to'g'ri kiriting: 
❌ AaBbCcDd harflardan tashqari harflarni kiritmang, yoki (javoblar soni {count_answer} tadan ko'p bo'lmasin)""",
        "ru": """Пожалуйста, введите ключи правильно:
❌ Используйте только буквы AaBbCcDd, не вводите другие символы или (количество ответов не должно превышать {count_answer}).

"""
    },
    "user_confirmed_answer": {
        "uz": """👤 {fullname}

✅ To'g'ri javoblar: {correct_answers}
❌ Noto'g'ri javoblar: {incorrect_answers}

📊 Sifat darajasi: {percent}%

📝 Xato javoblar raqami: <code>{indexes}</code>

📆 {now_date}

📡 @imtihonmarkazi
🤖 <a href="t.me/imtihonmarkazibot?start=">@imtihonmarkazibot</a>""",
        "ru": """👤 {fullname}

✅ Правильные ответы: {correct_answers}
❌ Неправильные ответы: {incorrect_answers}

📊 Уровень достижения: {percent}%

📝 Номера неправильных ответов: <code>{indexes}</code>

📆 {now_date}

📡 @imtihonmarkazi
🤖 <a href="t.me/imtihonmarkazibot?start=">@imtihonmarkazibot</a>"""
    },
    "user_subject_request_answer": {
        "uz": """<b>"{subject_name}"</b> fanidan {variant_id}-variant testida {count_answer} ta savol bor

Marhamat o'z javoblaringizni yuboring
Javoblarni quyidagi namunadek yuboring

abcdaBacAac...""",
        "ru": """В тесте по <b>"{subject_name}"</b> {count_answer} вопросов.

Пожалуйста, отправьте ваши ответы.
Отправляйте ответы в следующем формате:

abcdaBacAac...""",
    },
    "user_request_subject_id": {
        "uz": """🆔 Test ID raqamini kiriting:""",
        "ru": """🆔 Введите ID номер теста:""",
    },
    "user_full_subject": {
        "uz": "<b>📚 \"Blok fanlardan test\"</b> ishlash uchun iltimos test tilini tanlang...",
        "ru": "📚 <b>\"Тест по предметам блока\"</b>, для прохождения, пожалуйста, сначала выберите язык теста..."
    },
    "user_select_subject_type": {
        "uz": "<i>Marhamat, o'zingizga ma'qul test formatini tanlang:</i>",
        "ru": "<i>Пожалуйста, выберите предпочитаемый формат теста:</i>"
    },
    "user_subject_subject": {
        "uz": "📕 Quyidagi menularidan birini tanlang",
        "ru": "📕 Выберите одно из следующих меню"
    },
    "user_waiting_variant": {
        "uz": "⏳ Test yuklanmoqda. Iltimos kuting!",
        "ru": "⏳ Загрузка теста. Пожалуйста, подождите!"
    },
    "user_default_share": {
        "uz": """<b>Do'stim, men barcha fandan yangi testlar topdim!</b>

🔗 Ushbu havola orqali o'ting va <b>istalgan fandan</b> yangi (PDF) testni yuklab oling hamda <b>kalitlarni botga yuborib</b> bilimingizni sinovdan o'tkazing!

👉 <b><a href='{USERNAME_START}share'>@imtihonmarkazibot</a></b>""",
        "ru": """<b>Привет, я нашел новые тесты по всем предметам!</b>

🔗 Перейдите по этой ссылке, скачайте новый тест (PDF) по <b>любому предмету</b> и проверьте свои знания, <b>отправив ключи боту</b>!

👉 <b><a href='{USERNAME_START}share'>@imtihonmarkazibot</a></b>"""
    },
    "user_share_text": {
        "uz": """<b>Do'stim, men ({subject_lang}) {subject_name} fanidan yangi test topdim!</b>

🔗 Ushbu havola orqali o'ting va <b>({subject_lang}) {subject_name}</b> fanidan yangi (PDF) testni yuklab oling hamda <b>kalitlarni botga yuborib</b> bilimingizni sinovdan o'tkazing!

👉 <b><a href='{USERNAME_START}exam_{subject_id}'>@imtihonmarkazibot</a></b>""",
        "ru": """<b>Привет, я нашел новый тест в ({subject_lang}) {subject_name}!</b>

🔗 Перейдите по этой ссылке, загрузите новый тест (PDF) с сайта <b>({subject_lang}) {subject_name}</b> и проверьте свои знания, <b>отправив ключи боту</b>!

👉 <b><a href='{USERNAME_START}exam_{subject_id}'>@imtihonmarkazibot</a></b>"""
    },
    "user_click_me": {
        "uz": "Ustiga bosing!",
        "ru": "Нажмите здесь!"
    },
    "user_select_first_subject": {
        "uz": "1-Fan (mutaxassislik)ni ko’rsating:",
        "ru": "Укажите 1-й предмет (специальность):"
    },
    "select_related_subjects": {
        "uz": "2-Fan (mutaxassislik)ni ko'rsating:",
        "ru": "Укажите 2-й предмет (специальность):"
    },
}
_translated_buttons = {
    "user_check_subscribe": {
        "uz": "✅ Obunani tekshirish",
        "ru": "✅ Проверить подписку"
    },
    "user_solve_online_subject": {
        "uz": "💻 Onlayn test yechish",
        "ru": "💻 Онлайн-тест"
    },
    "user_subject_subject": {
        "uz": "📕 Alohida fanlardan test",
        "ru": "📕 Тест по отдельным предметам"
    },
    "user_full_subject": {
        "uz": "📚 Blok fanlardan test",
        "ru": "📚 Тест по предметам блока"
    },
    "user_get_subject": {
        "uz": "📥 Testlarni olish (PDF)",
        "ru": "📥 Скачать тесты (PDF)"
    },
    "user_check_answer": {
        "uz": "🔍 Javoblarni tekshirish",
        "ru": "🔍 Проверьте ответы"
    },
    "user_share_variant": {
        "uz": "♻️ Do'stlarga ulashish",
        "ru": "♻️ Поделиться"
    },
    "user_confirmation": {
        "uz": "✅ Tasdiqlash",
        "ru": "✅ Подтверждение"
    },
    "user_retype_answer": {
        "uz": "♻️ Qayta kiritish",
        "ru": "♻️ Переотправить"
    },
    "user_cancel_answer": {
        "uz": "❌ Bekor qilish",
        "ru": "❌ Останавить"
    },
    "user_settings": {
        "uz": "⚙️ Sozlamalar",
        "ru": "⚙️ Настройки"
    },
    "user_phone_number": {
        "uz": "📲 Raqam yuborish",
        "ru": "📲 Отправить номер"
    },
    "user_settings_name": {
        "uz": "👤 Ismni o'zgartirish",
        "ru": "👤 Изменить имя"
    },
    "user_settings_region": {
        "uz": "📍 Viloyatni o'zgartirish",
        "ru": "📍 Изменить регион"
    },
    "user_settings_district": {
        "uz": "🏙 Tumanni o'zgartirish",
        "ru": "🏙 Изменить район"
    },
    "user_settings_language": {
        "uz": "🇷🇺 Русский",
        "ru": "🇺🇿 O'zbek"
    },
    "user_settings_phone": {
        "uz": "🤳 Raqamni o'zgartirish",
        "ru": "🤳 Изменить номер"
    },
    "user_back": {
        "uz": "🔙 Ortga",
        "ru": "🔙 Назад"
    },
    "user_2_back": {
        "uz": "🔙  Ortga",
        "ru": "🔙  Назад"
    },
    "user_3_back": {
        "uz": "🔙Ortga",
        "ru": "🔙Назад"
    }
}

def text(key, lang):
    return _translated_texts[key][lang]


def button(key, lang):
    return _translated_buttons[key][lang]


def buttons(key):
    return tuple(_translated_buttons[key].values())
