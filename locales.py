"""
MemeMakerBot - Localization (i18n)
Full RU/EN support with auto-detection
"""
from typing import Dict

TEXTS: Dict[str, Dict[str, str]] = {
    # === Common ===
    "welcome": {
        "ru": "👋 <b>Привет!</b>\n\nЯ создаю мемы. Выбери шаблон и добавь свой текст.\n\n➡️ Нажми кнопку ниже, чтобы начать.",
        "en": "👋 <b>Hello!</b>\n\nI create memes. Pick a template and add your text.\n\n➡️ Press the button below to start.",
    },
    "help": {
        "ru": "📖 <b>Как пользоваться:</b>\n\n1️⃣ Выбери шаблон\n2️⃣ Введи текст (верх/низ)\n3️⃣ Получи мем!\n\n<b>Команды:</b>\n/start — начать\n/create — создать мем\n/help — справка",
        "en": "📖 <b>How to use:</b>\n\n1️⃣ Pick a template\n2️⃣ Enter text (top/bottom)\n3️⃣ Get your meme!\n\n<b>Commands:</b>\n/start — start\n/create — create meme\n/help — help",
    },
    
    # === Buttons ===
    "btn_create": {
        "ru": "🎨 Создать мем",
        "en": "🎨 Create meme",
    },
    "btn_help": {
        "ru": "❓ Помощь",
        "en": "❓ Help",
    },
    "btn_back": {
        "ru": "◀️ Назад",
        "en": "◀️ Back",
    },
    "btn_cancel": {
        "ru": "❌ Отмена",
        "en": "❌ Cancel",
    },
    "btn_skip": {
        "ru": "⏭ Пропустить",
        "en": "⏭ Skip",
    },
    "btn_generate": {
        "ru": "✨ Создать",
        "en": "✨ Generate",
    },
    "btn_again": {
        "ru": "🔄 Ещё мем",
        "en": "🔄 Another meme",
    },
    "btn_upload": {
        "ru": "📤 Загрузить своё",
        "en": "📤 Upload custom",
    },
    "btn_my_memes": {
        "ru": "📁 Мои мемы",
        "en": "📁 My memes",
    },
    "btn_prev": {
        "ru": "◀️ Назад",
        "en": "◀️ Prev",
    },
    "btn_next": {
        "ru": "▶️ Далее",
        "en": "▶️ Next",
    },
    "btn_select": {
        "ru": "Выбрать",
        "en": "Select",
    },
    "btn_custom_position": {
        "ru": "📍 Ввести координаты",
        "en": "📍 Enter coordinates",
    },
    "btn_auto_size": {
        "ru": "🔄 Авто (рекомендуется)",
        "en": "🔄 Auto (recommended)",
    },
    "btn_add_text": {
        "ru": "➕ Добавить ещё текст",
        "en": "➕ Add more text",
    },
    "btn_generate_now": {
        "ru": "✨ Создать мем",
        "en": "✨ Generate meme",
    },
    
    # === Meme Creation Flow ===
    "select_template": {
        "ru": "🖼 <b>Выбери шаблон:</b>\n\nСтраница {page}/{total}",
        "en": "🖼 <b>Select template:</b>\n\nPage {page}/{total}",
    },
    "enter_text": {
        "ru": "✏️ <b>Введи текст #{num}</b>\n\n📐 Размер: {width}×{height} px",
        "en": "✏️ <b>Enter text #{num}</b>\n\n📐 Size: {width}×{height} px",
    },
    "enter_top_text": {
        "ru": "✏️ <b>Введи текст сверху</b>\n\nИли нажми «Пропустить»",
        "en": "✏️ <b>Enter top text</b>\n\nOr press «Skip»",
    },
    "enter_bottom_text": {
        "ru": "✏️ <b>Введи текст снизу</b>\n\nИли нажми «Пропустить»",
        "en": "✏️ <b>Enter bottom text</b>\n\nOr press «Skip»",
    },
    "enter_text_num": {
        "ru": "✏️ <b>Введи текст #{num}</b>",
        "en": "✏️ <b>Enter text #{num}</b>",
    },
    "choose_position_8": {
        "ru": "📍 <b>Выбери позицию текста:</b>\n\n⬆️ — сверху по центру\n⬅️ 1-4 — слева (сверху вниз)\n➡️ 1-4 — справа (сверху вниз)\n⬇️ — снизу по центру",
        "en": "📍 <b>Choose text position:</b>\n\n⬆️ — top center\n⬅️ 1-4 — left side (top to bottom)\n➡️ 1-4 — right side (top to bottom)\n⬇️ — bottom center",
    },
    "choose_font_size_simple": {
        "ru": "🔤 <b>Выбери размер шрифта:</b>",
        "en": "🔤 <b>Choose font size:</b>",
    },
    "text_added": {
        "ru": "✅ <b>Текст #{num} добавлен!</b>\n\nДобавить ещё текст или создать мем?",
        "en": "✅ <b>Text #{num} added!</b>\n\nAdd more text or generate meme?",
    },
    "choose_position": {
        "ru": "📍 <b>Выбери позицию текста</b>\n\nИспользуй стрелки или введи координаты вручную.\n\n<i>Текст:</i> «{text}»",
        "en": "📍 <b>Choose text position</b>\n\nUse arrows or enter coordinates manually.\n\n<i>Text:</i> «{text}»",
    },
    "enter_x_coord": {
        "ru": "📍 <b>Введи X координату</b> (0-{max})\n\n<i>-1 = по центру</i>",
        "en": "📍 <b>Enter X coordinate</b> (0-{max})\n\n<i>-1 = centered</i>",
    },
    "enter_y_coord": {
        "ru": "📍 <b>Введи Y координату</b> (0-{max})",
        "en": "📍 <b>Enter Y coordinate</b> (0-{max})",
    },
    "choose_font_size": {
        "ru": "🔤 <b>Выбери размер шрифта</b>\n\n🔹 S — маленький\n🔸 M — средний\n🔶 L — большой\n🔄 Auto — подберётся автоматически",
        "en": "🔤 <b>Choose font size</b>\n\n🔹 S — small\n🔸 M — medium\n🔶 L — large\n🔄 Auto — automatic",
    },
    "confirm_add_more": {
        "ru": "✅ <b>Текст #{num} добавлен!</b>\n\nДобавить ещё текст или создать мем?",
        "en": "✅ <b>Text #{num} added!</b>\n\nAdd more text or generate meme?",
    },
    "invalid_coordinate": {
        "ru": "❌ Неверная координата. Введи число от {min} до {max}",
        "en": "❌ Invalid coordinate. Enter a number from {min} to {max}",
    },
    "generating": {
        "ru": "⏳ Генерирую мем...",
        "en": "⏳ Generating meme...",
    },
    "meme_ready": {
        "ru": "✅ <b>Готово!</b>",
        "en": "✅ <b>Done!</b>",
    },
    "cancelled": {
        "ru": "❌ Отменено",
        "en": "❌ Cancelled",
    },
    "upload_image": {
        "ru": "📤 <b>Отправь изображение</b>\n\nФормат: JPG, PNG, WebP\nМакс. размер: 10 МБ",
        "en": "📤 <b>Send an image</b>\n\nFormat: JPG, PNG, WebP\nMax size: 10 MB",
    },
    "image_received": {
        "ru": "✅ Изображение получено!",
        "en": "✅ Image received!",
    },
    "no_text_warning": {
        "ru": "⚠️ Нужен текст хотя бы сверху или снизу!",
        "en": "⚠️ You need text at least on top or bottom!",
    },
    
    # === Errors ===
    "error_generic": {
        "ru": "❌ Произошла ошибка. Попробуй ещё раз.",
        "en": "❌ An error occurred. Please try again.",
    },
    "error_rate_limit": {
        "ru": "⏰ Слишком много запросов. Подожди немного.",
        "en": "⏰ Too many requests. Please wait a moment.",
    },
    "error_text_too_long": {
        "ru": "❌ Текст слишком длинный (макс. {max} символов)",
        "en": "❌ Text is too long (max {max} characters)",
    },
    "error_invalid_image": {
        "ru": "❌ Неверный формат изображения",
        "en": "❌ Invalid image format",
    },
    "error_image_too_large": {
        "ru": "❌ Изображение слишком большое (макс. {max} МБ)",
        "en": "❌ Image is too large (max {max} MB)",
    },
    "no_templates": {
        "ru": "😔 Шаблоны не найдены.\n\nПопросите администратора добавить шаблоны.",
        "en": "😔 No templates found.\n\nAsk the admin to add templates.",
    },
    
    # === Admin ===
    "admin_welcome": {
        "ru": "🔐 <b>Админ-панель</b>\n\n👤 Пользователей: <b>{users}</b>\n🖼 Мемов создано: <b>{memes}</b>\n❌ Ошибок: <b>{errors}</b>",
        "en": "🔐 <b>Admin Panel</b>\n\n👤 Users: <b>{users}</b>\n🖼 Memes created: <b>{memes}</b>\n❌ Errors: <b>{errors}</b>",
    },
    "admin_stats": {
        "ru": "📊 <b>Статистика</b>\n\n👤 Пользователей: <b>{users}</b>\n🖼 Мемов создано: <b>{memes}</b>\n📁 Шаблонов: <b>{templates}</b>\n❌ Ошибок: <b>{errors}</b>",
        "en": "📊 <b>Statistics</b>\n\n👤 Users: <b>{users}</b>\n🖼 Memes created: <b>{memes}</b>\n📁 Templates: <b>{templates}</b>\n❌ Errors: <b>{errors}</b>",
    },
    "admin_templates": {
        "ru": "🖼 <b>Управление шаблонами</b>\n\nВсего: <b>{count}</b>\n\n✅ = активен | ❌ = скрыт",
        "en": "🖼 <b>Manage Templates</b>\n\nTotal: <b>{count}</b>\n\n✅ = active | ❌ = hidden",
    },
    "admin_broadcast": {
        "ru": "📢 <b>Рассылка</b>\n\nОтправь сообщение для рассылки всем пользователям:",
        "en": "📢 <b>Broadcast</b>\n\nSend a message to broadcast to all users:",
    },
    "admin_broadcast_confirm": {
        "ru": "📢 Отправить <b>{count}</b> пользователям?\n\nСообщение:\n<i>{preview}</i>",
        "en": "📢 Send to <b>{count}</b> users?\n\nMessage:\n<i>{preview}</i>",
    },
    "admin_broadcast_done": {
        "ru": "✅ <b>Рассылка завершена</b>\n\nОтправлено: <b>{sent}</b> / {total}",
        "en": "✅ <b>Broadcast complete</b>\n\nSent: <b>{sent}</b> / {total}",
    },
    "admin_broadcast_sending": {
        "ru": "📤 Отправка... {current}/{total}",
        "en": "📤 Sending... {current}/{total}",
    },
    "admin_template_added": {
        "ru": "✅ Шаблон «{name}» добавлен!",
        "en": "✅ Template «{name}» added!",
    },
    "admin_template_deleted": {
        "ru": "🗑 Шаблон удалён",
        "en": "🗑 Template deleted",
    },
    "admin_template_toggled": {
        "ru": "Статус шаблона изменён",
        "en": "Template status changed",
    },
    "admin_access_denied": {
        "ru": "🚫 Доступ запрещён",
        "en": "🚫 Access denied",
    },
    "admin_add_template_prompt": {
        "ru": "📤 <b>Добавление шаблона</b>\n\nОтправь изображение.\nВ подписи укажи название шаблона.",
        "en": "📤 <b>Add Template</b>\n\nSend an image.\nAdd template name in the caption.",
    },
    "admin_settings": {
        "ru": "⚙️ <b>Настройки</b>\n\n📊 Rate limit: <b>{rate_limit}</b> сообщений / {rate_period} сек\n📝 Макс. длина текста: <b>{max_text}</b> символов\n🖼 Шаблонов на странице: <b>{per_page}</b>",
        "en": "⚙️ <b>Settings</b>\n\n📊 Rate limit: <b>{rate_limit}</b> messages / {rate_period} sec\n📝 Max text length: <b>{max_text}</b> characters\n🖼 Templates per page: <b>{per_page}</b>",
    },
    "admin_no_message": {
        "ru": "❌ Сообщение для рассылки пустое",
        "en": "❌ Broadcast message is empty",
    },
    
    # === Admin Buttons ===
    "btn_admin_stats": {
        "ru": "📊 Статистика",
        "en": "📊 Statistics",
    },
    "btn_admin_templates": {
        "ru": "🖼 Шаблоны",
        "en": "🖼 Templates",
    },
    "btn_admin_broadcast": {
        "ru": "📢 Рассылка",
        "en": "📢 Broadcast",
    },
    "btn_admin_settings": {
        "ru": "⚙️ Настройки",
        "en": "⚙️ Settings",
    },
    "btn_admin_add_template": {
        "ru": "➕ Добавить шаблон",
        "en": "➕ Add template",
    },
    "btn_confirm": {
        "ru": "✅ Подтвердить",
        "en": "✅ Confirm",
    },
    "btn_admin_back": {
        "ru": "◀️ В админку",
        "en": "◀️ Back to admin",
    },
    
    # === User Upload to Catalog ===
    "btn_add_to_catalog": {
        "ru": "➕ Добавить мем в каталог",
        "en": "➕ Add meme to catalog",
    },
    "upload_to_catalog": {
        "ru": "📤 <b>Добавление мема в каталог</b>\n\nОтправь изображение, которое станет шаблоном для всех.\n\n📏 Размер: от 200x200 до 4096x4096\n📁 Формат: JPG, PNG, WebP",
        "en": "📤 <b>Add meme to catalog</b>\n\nSend an image that will become a template for everyone.\n\n📏 Size: 200x200 to 4096x4096\n📁 Format: JPG, PNG, WebP",
    },
    "upload_enter_name": {
        "ru": "✏️ <b>Введи название для мема</b>\n\nНапример: «Грустный кот» или «Дрейк выбирает»",
        "en": "✏️ <b>Enter a name for the meme</b>\n\nFor example: «Sad cat» or «Drake choosing»",
    },
    "upload_limit_reached": {
        "ru": "⚠️ Ты уже загрузил {count}/{max} мемов сегодня.\n\nПопробуй завтра!",
        "en": "⚠️ You've already uploaded {count}/{max} memes today.\n\nTry tomorrow!",
    },
    "upload_pending_moderation": {
        "ru": "✅ <b>Мем отправлен на модерацию!</b>\n\nПосле проверки он появится в общем каталоге.",
        "en": "✅ <b>Meme sent for moderation!</b>\n\nAfter review, it will appear in the catalog.",
    },
    "upload_image_too_small": {
        "ru": "❌ Изображение слишком маленькое.\n\nМинимум: 200x200 пикселей",
        "en": "❌ Image is too small.\n\nMinimum: 200x200 pixels",
    },
    "upload_image_too_big": {
        "ru": "❌ Изображение слишком большое.\n\nМаксимум: 4096x4096 пикселей",
        "en": "❌ Image is too big.\n\nMaximum: 4096x4096 pixels",
    },
    "upload_name_too_short": {
        "ru": "❌ Название слишком короткое (минимум 2 символа)",
        "en": "❌ Name is too short (minimum 2 characters)",
    },
    "upload_name_too_long": {
        "ru": "❌ Название слишком длинное (максимум 50 символов)",
        "en": "❌ Name is too long (maximum 50 characters)",
    },
    
    # === Admin Moderation ===
    "btn_admin_moderation": {
        "ru": "🔍 Модерация ({count})",
        "en": "🔍 Moderation ({count})",
    },
    "admin_moderation_title": {
        "ru": "🔍 <b>Модерация мемов</b>\n\nНа рассмотрении: <b>{count}</b>",
        "en": "🔍 <b>Meme Moderation</b>\n\nPending: <b>{count}</b>",
    },
    "admin_moderation_empty": {
        "ru": "✅ Нет мемов на модерации",
        "en": "✅ No memes pending moderation",
    },
    "admin_moderation_item": {
        "ru": "📝 <b>{name}</b>\n👤 От: {user_id}",
        "en": "📝 <b>{name}</b>\n👤 From: {user_id}",
    },
    "btn_approve": {
        "ru": "✅ Одобрить",
        "en": "✅ Approve",
    },
    "btn_reject": {
        "ru": "❌ Отклонить",
        "en": "❌ Reject",
    },
    "admin_approved": {
        "ru": "✅ Мем одобрен и добавлен в каталог!",
        "en": "✅ Meme approved and added to catalog!",
    },
    "admin_rejected": {
        "ru": "❌ Мем отклонён",
        "en": "❌ Meme rejected",
    },
}


def get_text(key: str, lang: str = "ru", **kwargs) -> str:
    """Get localized text by key."""
    lang = lang if lang in ("ru", "en") else "ru"
    text = TEXTS.get(key, {}).get(lang, TEXTS.get(key, {}).get("ru", key))
    if kwargs:
        try:
            text = text.format(**kwargs)
        except (KeyError, ValueError):
            pass
    return text


def detect_language(language_code: str | None) -> str:
    """Detect user language from Telegram language_code."""
    if not language_code:
        return "ru"
    # Support more English variants
    if language_code.lower().startswith(("en", "gb", "us", "au")):
        return "en"
    return "ru"
