"""EduLingua AI — Internationalization (i18n) module.

Supports Russian, Uzbek, and English interface languages.
"""

from __future__ import annotations

from typing import Any

# Supported interface languages
SUPPORTED_LANGUAGES = {"ru", "uz", "en"}
DEFAULT_LANGUAGE = "ru"

# ──────────────────────────────────────────────────────────────
# Translation strings organized by language → key
# ──────────────────────────────────────────────────────────────

_TRANSLATIONS: dict[str, dict[str, str]] = {
    # ── Russian ──────────────────────────────────────────────
    "ru": {
        # Language selection
        "choose_language": "🌐 Выберите язык интерфейса:",
        "language_set": "✅ Язык интерфейса установлен: Русский 🇷🇺",
        "lang_russian": "🇷🇺 Русский",
        "lang_uzbek": "🇺🇿 Ўзбекча",
        "lang_english": "🇬🇧 English",

        # Welcome
        "welcome": (
            "👋 Добро пожаловать в <b>EduLingua AI</b>!\n\n"
            "🎓 Я — ваш умный образовательный помощник.\n\n"
            "Выберите, с чего хотите начать:"
        ),
        "welcome_back": "👋 С возвращением, <b>{name}</b>!\n\nВыберите действие:",

        # Main menu
        "main_menu": "📋 Главное меню",
        "btn_eduai": "🎓 EduAI — ИИ-репетитор",
        "btn_lingua": "🌍 LinguaBot — Изучение языков",
        "btn_progress": "📊 Мой прогресс",
        "btn_daily": "🔥 Ежедневные задания",
        "btn_leaderboard": "🏆 Рейтинг",
        "btn_premium": "💎 Premium",
        "btn_profile": "👤 Мой профиль",
        "btn_settings": "⚙️ Настройки",
        "btn_help": "❓ Помощь",
        "btn_back": "⬅️ Назад",
        "btn_main_menu": "🏠 Главное меню",

        # EduAI
        "eduai_menu": (
            "🎓 <b>EduAI — ИИ-Репетитор</b>\n\n"
            "Выберите предмет или задайте вопрос прямо здесь.\n"
            "Вы также можете отправить фото задачи."
        ),
        "select_subject": "📚 Выберите предмет:",
        "subject_selected": "📘 Предмет: <b>{subject}</b>\n\nЗадайте вопрос или отправьте фото задачи.",
        "btn_explain_simpler": "🔄 Объясни проще",
        "btn_another_method": "💡 Другой способ",
        "btn_hint": "🤔 Подсказка",
        "btn_check_answer": "✅ Проверь мой ответ",
        "btn_similar_task": "📝 Похожая задача",
        "btn_math": "📐 Математика",
        "btn_algebra": "📊 Алгебра",
        "btn_geometry": "📏 Геометрия",
        "btn_physics": "⚛️ Физика",
        "btn_chemistry": "🧪 Химия",
        "btn_biology": "🧬 Биология",
        "btn_history": "📜 История",
        "btn_geography": "🌍 География",
        "btn_informatics": "💻 Информатика",
        "btn_literature": "📖 Литература",
        "btn_russian_lang": "🇷🇺 Русский язык",
        "btn_english_lang": "🇬🇧 Английский язык",
        "processing": "⏳ Обрабатываю ваш запрос...",
        "ai_error": "❌ Произошла ошибка при обработке запроса. Попробуйте позже.",
        "ai_not_configured": (
            "⚠️ AI-провайдер не настроен.\n"
            "Администратор должен задать GEMINI_API_KEY."
        ),

        # LinguaBot
        "lingua_menu": (
            "🌍 <b>LinguaBot — Изучение языков</b>\n\n"
            "Выберите язык для изучения:"
        ),
        "select_learning_lang": "🌐 Какой язык хотите изучать?",
        "lingua_sections": (
            "📚 <b>{language}</b> — Выберите раздел:\n\n"
            "Ваш уровень: <b>{level}</b>"
        ),
        "btn_vocabulary": "📝 Словарный запас",
        "btn_grammar": "📖 Грамматика",
        "btn_speaking": "🗣 Разговорная практика",
        "btn_writing": "✍️ Письмо",
        "btn_listening": "🎧 Аудирование",
        "btn_level_test": "📋 Тест на уровень",
        "btn_lang_en": "🇬🇧 Английский",
        "btn_lang_ru": "🇷🇺 Русский",
        "btn_lang_uz": "🇺🇿 Узбекский",
        "btn_lang_de": "🇩🇪 Немецкий",
        "btn_lang_fr": "🇫🇷 Французский",
        "btn_lang_es": "🇪🇸 Испанский",
        "level_test_intro": (
            "📋 <b>Тест на определение уровня</b>\n\n"
            "Сейчас я задам несколько вопросов, чтобы определить ваш уровень.\n"
            "Отвечайте честно — это поможет подобрать подходящие задания."
        ),
        "level_result": "📊 Ваш уровень: <b>{level}</b>\n\n{description}",
        "vocab_new_word": (
            "📝 <b>Новое слово</b>\n\n"
            "🔤 <b>{word}</b>\n"
            "📖 <i>{translation}</i>\n\n"
            "💬 Пример: {example}"
        ),
        "speaking_scenario": (
            "🗣 <b>Разговорная практика</b>\n\n"
            "Сценарий: <b>{scenario}</b>\n\n"
            "{description}\n\n"
            "Начните разговор или выберите другой сценарий."
        ),
        "btn_scenario_intro": "👋 Знакомство",
        "btn_scenario_travel": "✈️ Путешествия",
        "btn_scenario_restaurant": "🍽 Ресторан",
        "btn_scenario_shop": "🛍 Магазин",
        "btn_scenario_work": "💼 Работа",
        "btn_scenario_study": "📚 Учёба",
        "btn_scenario_daily": "🏠 Повседневное общение",

        # Profile
        "profile_info": (
            "👤 <b>Мой профиль</b>\n\n"
            "📛 Имя: <b>{name}</b>\n"
            "🆔 Telegram ID: <code>{telegram_id}</code>\n"
            "📅 Регистрация: {registered}\n"
            "🌐 Язык интерфейса: {interface_lang}\n"
            "📚 Изучаемый язык: {learning_lang}\n"
            "📊 Уровень: {level}\n\n"
            "━━━━━━━━━━━━━━━━━━\n\n"
            "📝 Решено задач: <b>{tasks_solved}</b>\n"
            "✅ Правильных ответов: <b>{correct_answers}</b>\n"
            "📖 Завершённых уроков: <b>{lessons_completed}</b>\n"
            "📝 Изучено слов: <b>{words_learned}</b>\n\n"
            "━━━━━━━━━━━━━━━━━━\n\n"
            "⭐ XP: <b>{xp}</b>\n"
            "🎖 Уровень: <b>{user_level}</b>\n"
            "🔥 Дней активности: <b>{active_days}</b>\n"
            "💎 Подписка: <b>{subscription}</b>"
        ),

        # Progress
        "progress_title": (
            "📊 <b>Мой прогресс</b>\n\n"
            "{progress_bar}\n\n"
            "⭐ XP: <b>{xp}</b> / <b>{next_level_xp}</b>\n"
            "🎖 Уровень: <b>{level}</b>\n"
            "🔥 Серия: <b>{streak}</b> дней\n\n"
            "📈 Сегодня: <b>{today_xp}</b> XP\n"
            "📅 На этой неделе: <b>{week_xp}</b> XP"
        ),

        # Daily Tasks
        "daily_title": (
            "🔥 <b>Ежедневные задания</b>\n\n"
            "Выполняйте задания каждый день для получения XP!\n\n"
            "{tasks}"
        ),
        "daily_task_item": "{icon} {title} — {reward} XP {status}",
        "daily_completed": "✅",
        "daily_pending": "⬜",

        # Leaderboard
        "leaderboard_title": "🏆 <b>Рейтинг — {period}</b>\n\n{entries}",
        "leaderboard_entry": "{rank}. {medal} <b>{name}</b> — {xp} XP",
        "btn_daily_board": "📅 За день",
        "btn_weekly_board": "📆 За неделю",
        "btn_alltime_board": "🏅 За всё время",

        # Premium
        "premium_info": (
            "💎 <b>Premium подписки</b>\n\n"
            "Выберите тариф:\n\n"
            "🆓 <b>FREE</b> — Базовые возможности\n"
            "• {free_limit} AI-запросов в день\n"
            "• Базовые упражнения\n"
            "• Ограниченная статистика\n\n"
            "⭐ <b>PRO</b>\n"
            "• {pro_limit} AI-запросов в день\n"
            "• Полный доступ к обучению\n"
            "• Расширенная статистика\n\n"
            "👑 <b>ULTIMATE</b>\n"
            "• {ultimate_limit} AI-запросов в день\n"
            "• Все возможности\n"
            "• Индивидуальный план обучения\n"
            "• Приоритетная обработка"
        ),
        "btn_free_plan": "🆓 FREE",
        "btn_pro_plan": "⭐ PRO",
        "btn_ultimate_plan": "👑 ULTIMATE",
        "current_plan": "Ваш текущий тариф: <b>{plan}</b>",
        "payment_not_configured": "⚠️ Оплата временно недоступна. Обратитесь к администратору.",

        # Settings
        "settings_menu": (
            "⚙️ <b>Настройки</b>\n\n"
            "Текущий язык: {language}\n"
            "Изучаемый язык: {learning_lang}"
        ),
        "btn_change_lang": "🌐 Изменить язык интерфейса",
        "btn_change_learning_lang": "📚 Изменить изучаемый язык",
        "btn_reset_progress": "🔄 Сбросить прогресс",
        "reset_confirm": "⚠️ Вы уверены? Это действие нельзя отменить.",
        "btn_confirm_reset": "✅ Да, сбросить",
        "btn_cancel": "❌ Отмена",

        # Help
        "help_text": (
            "❓ <b>Помощь</b>\n\n"
            "🎓 <b>EduAI</b> — задавайте вопросы по учебным предметам, "
            "отправляйте фото задач.\n\n"
            "🌍 <b>LinguaBot</b> — изучайте иностранные языки "
            "с помощью ИИ.\n\n"
            "📊 <b>Прогресс</b> — следите за своими результатами.\n\n"
            "🔥 <b>Ежедневные задания</b> — выполняйте задания "
            "для получения XP.\n\n"
            "🏆 <b>Рейтинг</b> — соревнуйтесь с другими "
            "пользователями.\n\n"
            "💎 <b>Premium</b> — расширенные возможности.\n\n"
            "Если нужна помощь, напишите /help."
        ),

        # Errors
        "error_generic": "❌ Произошла ошибка. Попробуйте позже.",
        "error_rate_limit": "⏳ Слишком много запросов. Подождите {seconds} секунд.",
        "error_daily_limit": "📊 Вы исчерпали дневной лимит AI-запросов ({limit}). Обновите подписку для увеличения.",
        "error_not_authorized": "🚫 У вас нет доступа к этой функции.",
        "error_blocked": "🚫 Ваш аккаунт заблокирован. Обратитесь к администратору.",

        # Gamification
        "xp_earned": "⭐ +{xp} XP!",
        "level_up": "🎉 Поздравляем! Вы достигли уровня <b>{level}</b>!",
        "achievement_unlocked": "🏆 Достижение разблокировано: <b>{title}</b>!\n{description}",
        "streak_reminder": "🔥 Не забудьте позаниматься сегодня, чтобы сохранить серию!",
    },

    # ── Uzbek ────────────────────────────────────────────────
    "uz": {
        "choose_language": "🌐 Interfeys tilini tanlang:",
        "language_set": "✅ Interfeys tili o'rnatildi: O'zbekcha 🇺🇿",
        "lang_russian": "🇷🇺 Русский",
        "lang_uzbek": "🇺🇿 Ўзбекча",
        "lang_english": "🇬🇧 English",
        "welcome": (
            "👋 <b>EduLingua AI</b>ga xush kelibsiz!\n\n"
            "🎓 Men — sizning aqlli ta'lim yordamchingizman.\n\n"
            "Nimadan boshlashni tanlang:"
        ),
        "welcome_back": "👋 Qaytganingizdan xursandmiz, <b>{name}</b>!\n\nAmalni tanlang:",
        "main_menu": "📋 Asosiy menyu",
        "btn_eduai": "🎓 EduAI — AI-repetitor",
        "btn_lingua": "🌍 LinguaBot — Til o'rganish",
        "btn_progress": "📊 Mening taraqqiyotim",
        "btn_daily": "🔥 Kunlik topshiriqlar",
        "btn_leaderboard": "🏆 Reyting",
        "btn_premium": "💎 Premium",
        "btn_profile": "👤 Mening profilim",
        "btn_settings": "⚙️ Sozlamalar",
        "btn_help": "❓ Yordam",
        "btn_back": "⬅️ Orqaga",
        "btn_main_menu": "🏠 Asosiy menyu",
        "eduai_menu": (
            "🎓 <b>EduAI — AI-Repetitor</b>\n\n"
            "Fanni tanlang yoki savolingizni shu yerda bering.\n"
            "Shuningdek, masala rasmini yuborishingiz mumkin."
        ),
        "select_subject": "📚 Fanni tanlang:",
        "subject_selected": "📘 Fan: <b>{subject}</b>\n\nSavol bering yoki masala rasmini yuboring.",
        "btn_explain_simpler": "🔄 Soddaroq tushuntir",
        "btn_another_method": "💡 Boshqa usul",
        "btn_hint": "🤔 Maslahat",
        "btn_check_answer": "✅ Javobimni tekshir",
        "btn_similar_task": "📝 O'xshash masala",
        "btn_math": "📐 Matematika",
        "btn_algebra": "📊 Algebra",
        "btn_geometry": "📏 Geometriya",
        "btn_physics": "⚛️ Fizika",
        "btn_chemistry": "🧪 Kimyo",
        "btn_biology": "🧬 Biologiya",
        "btn_history": "📜 Tarix",
        "btn_geography": "🌍 Geografiya",
        "btn_informatics": "💻 Informatika",
        "btn_literature": "📖 Adabiyot",
        "btn_russian_lang": "🇷🇺 Rus tili",
        "btn_english_lang": "🇬🇧 Ingliz tili",
        "processing": "⏳ So'rovingiz qayta ishlanmoqda...",
        "ai_error": "❌ So'rovni qayta ishlashda xatolik yuz berdi. Keyinroq urinib ko'ring.",
        "ai_not_configured": "⚠️ AI-provayder sozlanmagan.\nAdministrator GEMINI_API_KEY ni o'rnatishi kerak.",
        "lingua_menu": "🌍 <b>LinguaBot — Til o'rganish</b>\n\nO'rganish uchun tilni tanlang:",
        "select_learning_lang": "🌐 Qaysi tilni o'rganmoqchisiz?",
        "lingua_sections": "📚 <b>{language}</b> — Bo'limni tanlang:\n\nSizning darajangiz: <b>{level}</b>",
        "btn_vocabulary": "📝 Lug'at boyligi",
        "btn_grammar": "📖 Grammatika",
        "btn_speaking": "🗣 So'zlashuv amaliyoti",
        "btn_writing": "✍️ Yozuv",
        "btn_listening": "🎧 Tinglash",
        "btn_level_test": "📋 Daraja testi",
        "btn_lang_en": "🇬🇧 Ingliz tili",
        "btn_lang_ru": "🇷🇺 Rus tili",
        "btn_lang_uz": "🇺🇿 O'zbek tili",
        "btn_lang_de": "🇩🇪 Nemis tili",
        "btn_lang_fr": "🇫🇷 Fransuz tili",
        "btn_lang_es": "🇪🇸 Ispan tili",
        "level_test_intro": (
            "📋 <b>Daraja aniqlash testi</b>\n\n"
            "Darajangizni aniqlash uchun bir necha savol beraman.\n"
            "Rostgo'y javob bering — bu mos topshiriqlarni tanlashga yordam beradi."
        ),
        "level_result": "📊 Sizning darajangiz: <b>{level}</b>\n\n{description}",
        "vocab_new_word": "📝 <b>Yangi so'z</b>\n\n🔤 <b>{word}</b>\n📖 <i>{translation}</i>\n\n💬 Misol: {example}",
        "speaking_scenario": "🗣 <b>So'zlashuv amaliyoti</b>\n\nStsenariy: <b>{scenario}</b>\n\n{description}\n\nSuhbatni boshlang yoki boshqa stsenariy tanlang.",
        "btn_scenario_intro": "👋 Tanishuv",
        "btn_scenario_travel": "✈️ Sayohat",
        "btn_scenario_restaurant": "🍽 Restoran",
        "btn_scenario_shop": "🛍 Do'kon",
        "btn_scenario_work": "💼 Ish",
        "btn_scenario_study": "📚 O'qish",
        "btn_scenario_daily": "🏠 Kundalik muloqot",
        "profile_info": (
            "👤 <b>Mening profilim</b>\n\n"
            "📛 Ism: <b>{name}</b>\n"
            "🆔 Telegram ID: <code>{telegram_id}</code>\n"
            "📅 Ro'yxatdan o'tgan: {registered}\n"
            "🌐 Interfeys tili: {interface_lang}\n"
            "📚 O'rganilayotgan til: {learning_lang}\n"
            "📊 Daraja: {level}\n\n"
            "━━━━━━━━━━━━━━━━━━\n\n"
            "📝 Yechilgan masalalar: <b>{tasks_solved}</b>\n"
            "✅ To'g'ri javoblar: <b>{correct_answers}</b>\n"
            "📖 Tugallangan darslar: <b>{lessons_completed}</b>\n"
            "📝 O'rganilgan so'zlar: <b>{words_learned}</b>\n\n"
            "━━━━━━━━━━━━━━━━━━\n\n"
            "⭐ XP: <b>{xp}</b>\n"
            "🎖 Daraja: <b>{user_level}</b>\n"
            "🔥 Faol kunlar: <b>{active_days}</b>\n"
            "💎 Obuna: <b>{subscription}</b>"
        ),
        "progress_title": (
            "📊 <b>Mening taraqqiyotim</b>\n\n"
            "{progress_bar}\n\n"
            "⭐ XP: <b>{xp}</b> / <b>{next_level_xp}</b>\n"
            "🎖 Daraja: <b>{level}</b>\n"
            "🔥 Seriya: <b>{streak}</b> kun\n\n"
            "📈 Bugun: <b>{today_xp}</b> XP\n"
            "📅 Bu hafta: <b>{week_xp}</b> XP"
        ),
        "daily_title": "🔥 <b>Kunlik topshiriqlar</b>\n\nHar kuni topshiriqlarni bajaring va XP oling!\n\n{tasks}",
        "daily_task_item": "{icon} {title} — {reward} XP {status}",
        "daily_completed": "✅",
        "daily_pending": "⬜",
        "leaderboard_title": "🏆 <b>Reyting — {period}</b>\n\n{entries}",
        "leaderboard_entry": "{rank}. {medal} <b>{name}</b> — {xp} XP",
        "btn_daily_board": "📅 Kunlik",
        "btn_weekly_board": "📆 Haftalik",
        "btn_alltime_board": "🏅 Barchasi",
        "premium_info": (
            "💎 <b>Premium obunalar</b>\n\n"
            "Tarifni tanlang:\n\n"
            "🆓 <b>FREE</b> — Asosiy imkoniyatlar\n"
            "• {free_limit} AI-so'rov kuniga\n"
            "• Asosiy mashqlar\n"
            "• Cheklangan statistika\n\n"
            "⭐ <b>PRO</b>\n"
            "• {pro_limit} AI-so'rov kuniga\n"
            "• To'liq ta'lim imkoniyatlari\n"
            "• Kengaytirilgan statistika\n\n"
            "👑 <b>ULTIMATE</b>\n"
            "• {ultimate_limit} AI-so'rov kuniga\n"
            "• Barcha imkoniyatlar\n"
            "• Individual o'quv rejasi\n"
            "• Ustuvor qayta ishlash"
        ),
        "btn_free_plan": "🆓 FREE",
        "btn_pro_plan": "⭐ PRO",
        "btn_ultimate_plan": "👑 ULTIMATE",
        "current_plan": "Joriy tarifingiz: <b>{plan}</b>",
        "payment_not_configured": "⚠️ To'lov vaqtincha mavjud emas. Administratorga murojaat qiling.",
        "settings_menu": "⚙️ <b>Sozlamalar</b>\n\nJoriy til: {language}\nO'rganilayotgan til: {learning_lang}",
        "btn_change_lang": "🌐 Interfeys tilini o'zgartirish",
        "btn_change_learning_lang": "📚 O'rganilayotgan tilni o'zgartirish",
        "btn_reset_progress": "🔄 Taraqqiyotni tiklash",
        "reset_confirm": "⚠️ Ishonchingiz komilmi? Bu amalni bekor qilib bo'lmaydi.",
        "btn_confirm_reset": "✅ Ha, tiklash",
        "btn_cancel": "❌ Bekor qilish",
        "help_text": (
            "❓ <b>Yordam</b>\n\n"
            "🎓 <b>EduAI</b> — o'quv fanlari bo'yicha savollar bering, masala rasmlarini yuboring.\n\n"
            "🌍 <b>LinguaBot</b> — AI yordamida chet tillarini o'rganing.\n\n"
            "📊 <b>Taraqqiyot</b> — natijalaringizni kuzating.\n\n"
            "🔥 <b>Kunlik topshiriqlar</b> — XP olish uchun topshiriqlarni bajaring.\n\n"
            "🏆 <b>Reyting</b> — boshqa foydalanuvchilar bilan raqobatlashing.\n\n"
            "💎 <b>Premium</b> — kengaytirilgan imkoniyatlar.\n\n"
            "Yordam kerak bo'lsa, /help yozing."
        ),
        "error_generic": "❌ Xatolik yuz berdi. Keyinroq urinib ko'ring.",
        "error_rate_limit": "⏳ Juda ko'p so'rov. {seconds} soniya kuting.",
        "error_daily_limit": "📊 Kunlik AI-so'rovlar limitini tugatdingiz ({limit}). Obunani yangilang.",
        "error_not_authorized": "🚫 Sizda bu funksiyaga ruxsat yo'q.",
        "error_blocked": "🚫 Hisobingiz bloklangan. Administratorga murojaat qiling.",
        "xp_earned": "⭐ +{xp} XP!",
        "level_up": "🎉 Tabriklaymiz! Siz <b>{level}</b> darajaga yetdingiz!",
        "achievement_unlocked": "🏆 Yutuq ochildi: <b>{title}</b>!\n{description}",
        "streak_reminder": "🔥 Seriyani saqlab qolish uchun bugun shug'ullanishni unutmang!",
    },

    # ── English ──────────────────────────────────────────────
    "en": {
        "choose_language": "🌐 Choose interface language:",
        "language_set": "✅ Interface language set: English 🇬🇧",
        "lang_russian": "🇷🇺 Русский",
        "lang_uzbek": "🇺🇿 Ўзбекча",
        "lang_english": "🇬🇧 English",
        "welcome": (
            "👋 Welcome to <b>EduLingua AI</b>!\n\n"
            "🎓 I'm your smart educational assistant.\n\n"
            "Choose what you'd like to start with:"
        ),
        "welcome_back": "👋 Welcome back, <b>{name}</b>!\n\nChoose an action:",
        "main_menu": "📋 Main Menu",
        "btn_eduai": "🎓 EduAI — AI Tutor",
        "btn_lingua": "🌍 LinguaBot — Learn Languages",
        "btn_progress": "📊 My Progress",
        "btn_daily": "🔥 Daily Tasks",
        "btn_leaderboard": "🏆 Leaderboard",
        "btn_premium": "💎 Premium",
        "btn_profile": "👤 My Profile",
        "btn_settings": "⚙️ Settings",
        "btn_help": "❓ Help",
        "btn_back": "⬅️ Back",
        "btn_main_menu": "🏠 Main Menu",
        "eduai_menu": (
            "🎓 <b>EduAI — AI Tutor</b>\n\n"
            "Select a subject or ask a question right here.\n"
            "You can also send a photo of a problem."
        ),
        "select_subject": "📚 Select a subject:",
        "subject_selected": "📘 Subject: <b>{subject}</b>\n\nAsk a question or send a photo.",
        "btn_explain_simpler": "🔄 Explain simpler",
        "btn_another_method": "💡 Another method",
        "btn_hint": "🤔 Give a hint",
        "btn_check_answer": "✅ Check my answer",
        "btn_similar_task": "📝 Similar task",
        "btn_math": "📐 Mathematics",
        "btn_algebra": "📊 Algebra",
        "btn_geometry": "📏 Geometry",
        "btn_physics": "⚛️ Physics",
        "btn_chemistry": "🧪 Chemistry",
        "btn_biology": "🧬 Biology",
        "btn_history": "📜 History",
        "btn_geography": "🌍 Geography",
        "btn_informatics": "💻 Computer Science",
        "btn_literature": "📖 Literature",
        "btn_russian_lang": "🇷🇺 Russian Language",
        "btn_english_lang": "🇬🇧 English Language",
        "processing": "⏳ Processing your request...",
        "ai_error": "❌ An error occurred while processing. Please try again later.",
        "ai_not_configured": "⚠️ AI provider is not configured.\nAdmin needs to set GEMINI_API_KEY.",
        "lingua_menu": "🌍 <b>LinguaBot — Learn Languages</b>\n\nChoose a language to study:",
        "select_learning_lang": "🌐 Which language would you like to learn?",
        "lingua_sections": "📚 <b>{language}</b> — Choose a section:\n\nYour level: <b>{level}</b>",
        "btn_vocabulary": "📝 Vocabulary",
        "btn_grammar": "📖 Grammar",
        "btn_speaking": "🗣 Speaking Practice",
        "btn_writing": "✍️ Writing",
        "btn_listening": "🎧 Listening",
        "btn_level_test": "📋 Level Test",
        "btn_lang_en": "🇬🇧 English",
        "btn_lang_ru": "🇷🇺 Russian",
        "btn_lang_uz": "🇺🇿 Uzbek",
        "btn_lang_de": "🇩🇪 German",
        "btn_lang_fr": "🇫🇷 French",
        "btn_lang_es": "🇪🇸 Spanish",
        "level_test_intro": (
            "📋 <b>Level Assessment Test</b>\n\n"
            "I'll ask a few questions to determine your level.\n"
            "Answer honestly — this will help select suitable tasks."
        ),
        "level_result": "📊 Your level: <b>{level}</b>\n\n{description}",
        "vocab_new_word": "📝 <b>New Word</b>\n\n🔤 <b>{word}</b>\n📖 <i>{translation}</i>\n\n💬 Example: {example}",
        "speaking_scenario": "🗣 <b>Speaking Practice</b>\n\nScenario: <b>{scenario}</b>\n\n{description}\n\nStart a conversation or choose another scenario.",
        "btn_scenario_intro": "👋 Introduction",
        "btn_scenario_travel": "✈️ Travel",
        "btn_scenario_restaurant": "🍽 Restaurant",
        "btn_scenario_shop": "🛍 Shopping",
        "btn_scenario_work": "💼 Work",
        "btn_scenario_study": "📚 Study",
        "btn_scenario_daily": "🏠 Daily Conversation",
        "profile_info": (
            "👤 <b>My Profile</b>\n\n"
            "📛 Name: <b>{name}</b>\n"
            "🆔 Telegram ID: <code>{telegram_id}</code>\n"
            "📅 Registered: {registered}\n"
            "🌐 Interface language: {interface_lang}\n"
            "📚 Learning language: {learning_lang}\n"
            "📊 Level: {level}\n\n"
            "━━━━━━━━━━━━━━━━━━\n\n"
            "📝 Tasks solved: <b>{tasks_solved}</b>\n"
            "✅ Correct answers: <b>{correct_answers}</b>\n"
            "📖 Lessons completed: <b>{lessons_completed}</b>\n"
            "📝 Words learned: <b>{words_learned}</b>\n\n"
            "━━━━━━━━━━━━━━━━━━\n\n"
            "⭐ XP: <b>{xp}</b>\n"
            "🎖 Level: <b>{user_level}</b>\n"
            "🔥 Active days: <b>{active_days}</b>\n"
            "💎 Subscription: <b>{subscription}</b>"
        ),
        "progress_title": (
            "📊 <b>My Progress</b>\n\n"
            "{progress_bar}\n\n"
            "⭐ XP: <b>{xp}</b> / <b>{next_level_xp}</b>\n"
            "🎖 Level: <b>{level}</b>\n"
            "🔥 Streak: <b>{streak}</b> days\n\n"
            "📈 Today: <b>{today_xp}</b> XP\n"
            "📅 This week: <b>{week_xp}</b> XP"
        ),
        "daily_title": "🔥 <b>Daily Tasks</b>\n\nComplete tasks every day to earn XP!\n\n{tasks}",
        "daily_task_item": "{icon} {title} — {reward} XP {status}",
        "daily_completed": "✅",
        "daily_pending": "⬜",
        "leaderboard_title": "🏆 <b>Leaderboard — {period}</b>\n\n{entries}",
        "leaderboard_entry": "{rank}. {medal} <b>{name}</b> — {xp} XP",
        "btn_daily_board": "📅 Daily",
        "btn_weekly_board": "📆 Weekly",
        "btn_alltime_board": "🏅 All Time",
        "premium_info": (
            "💎 <b>Premium Subscriptions</b>\n\n"
            "Choose a plan:\n\n"
            "🆓 <b>FREE</b> — Basic features\n"
            "• {free_limit} AI requests per day\n"
            "• Basic exercises\n"
            "• Limited stats\n\n"
            "⭐ <b>PRO</b>\n"
            "• {pro_limit} AI requests per day\n"
            "• Full learning access\n"
            "• Extended stats\n\n"
            "👑 <b>ULTIMATE</b>\n"
            "• {ultimate_limit} AI requests per day\n"
            "• All features\n"
            "• Custom learning plan\n"
            "• Priority processing"
        ),
        "btn_free_plan": "🆓 FREE",
        "btn_pro_plan": "⭐ PRO",
        "btn_ultimate_plan": "👑 ULTIMATE",
        "current_plan": "Your current plan: <b>{plan}</b>",
        "payment_not_configured": "⚠️ Payments are temporarily unavailable. Contact admin.",
        "settings_menu": "⚙️ <b>Settings</b>\n\nCurrent language: {language}\nLearning language: {learning_lang}",
        "btn_change_lang": "🌐 Change interface language",
        "btn_change_learning_lang": "📚 Change learning language",
        "btn_reset_progress": "🔄 Reset progress",
        "reset_confirm": "⚠️ Are you sure? This cannot be undone.",
        "btn_confirm_reset": "✅ Yes, reset",
        "btn_cancel": "❌ Cancel",
        "help_text": (
            "❓ <b>Help</b>\n\n"
            "🎓 <b>EduAI</b> — ask questions about school subjects, send photos of problems.\n\n"
            "🌍 <b>LinguaBot</b> — learn foreign languages with AI.\n\n"
            "📊 <b>Progress</b> — track your results.\n\n"
            "🔥 <b>Daily Tasks</b> — complete tasks to earn XP.\n\n"
            "🏆 <b>Leaderboard</b> — compete with other users.\n\n"
            "💎 <b>Premium</b> — extended features.\n\n"
            "Need help? Type /help."
        ),
        "error_generic": "❌ An error occurred. Please try again later.",
        "error_rate_limit": "⏳ Too many requests. Please wait {seconds} seconds.",
        "error_daily_limit": "📊 You've reached your daily AI request limit ({limit}). Upgrade for more.",
        "error_not_authorized": "🚫 You don't have access to this feature.",
        "error_blocked": "🚫 Your account is blocked. Contact admin.",
        "xp_earned": "⭐ +{xp} XP!",
        "level_up": "🎉 Congratulations! You've reached level <b>{level}</b>!",
        "achievement_unlocked": "🏆 Achievement unlocked: <b>{title}</b>!\n{description}",
        "streak_reminder": "🔥 Don't forget to study today to keep your streak!",
    },
}


def t(key: str, lang: str = DEFAULT_LANGUAGE, **kwargs: Any) -> str:
    """Get translated string by key and language.

    Args:
        key: Translation key.
        lang: Language code ('ru', 'uz', 'en').
        **kwargs: Format parameters.

    Returns:
        Translated and formatted string.
    """
    lang = lang if lang in SUPPORTED_LANGUAGES else DEFAULT_LANGUAGE
    translations = _TRANSLATIONS.get(lang, _TRANSLATIONS[DEFAULT_LANGUAGE])
    text = translations.get(key)

    if text is None:
        # Fallback to default language
        text = _TRANSLATIONS[DEFAULT_LANGUAGE].get(key, f"[{key}]")

    if kwargs:
        try:
            text = text.format(**kwargs)
        except (KeyError, IndexError):
            pass

    return text


def get_language_name(code: str, interface_lang: str = DEFAULT_LANGUAGE) -> str:
    """Get human-readable language name."""
    names = {
        "ru": {"ru": "Русский", "uz": "Rus tili", "en": "Russian"},
        "uz": {"ru": "Узбекский", "uz": "O'zbek tili", "en": "Uzbek"},
        "en": {"ru": "Английский", "uz": "Ingliz tili", "en": "English"},
        "de": {"ru": "Немецкий", "uz": "Nemis tili", "en": "German"},
        "fr": {"ru": "Французский", "uz": "Fransuz tili", "en": "French"},
        "es": {"ru": "Испанский", "uz": "Ispan tili", "en": "Spanish"},
    }
    lang_names = names.get(code, {})
    return lang_names.get(interface_lang, code.upper())
