"""
MemeMakerBot - User Handlers
8-position text placement flow
"""
import logging
import json
import base64
import tempfile
from pathlib import Path

from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery, FSInputFile, InputSticker
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from config import MAX_TEXT_LENGTH, TEMPLATES_DIR, UPLOADS_DIR, MAX_UPLOADS_PER_DAY, MIN_IMAGE_SIZE
from database import (
    get_active_templates, get_template_by_id, 
    increment_template_usage, save_meme,
    get_user_uploads_today, increment_user_uploads, add_user_template
)
from generator import generate_meme, TextBlock
from keyboards import (
    main_menu_kb, template_carousel_kb, text_input_kb, 
    result_kb, cancel_kb, upload_name_kb, font_size_kb,
    position_kb, add_more_text_kb
)
from locales import get_text, detect_language
from states import MemeCreation, MemeUpload

logger = logging.getLogger(__name__)
router = Router()


# ═══════════════════════════════════════════════
# WEB APP DATA HANDLER
# ═══════════════════════════════════════════════

@router.message(F.web_app_data)
async def handle_web_app_data(message: Message, state: FSMContext, bot: Bot):
    """Handle data from Mini App."""
    try:
        data = json.loads(message.web_app_data.data)
        action = data.get('action')
        
        if action == 'create_meme':
            # User wants to create meme from template
            filename = data.get('filename')
            if filename:
                template_path = UPLOADS_DIR / filename
                if template_path.exists():
                    await state.update_data(
                        template_path=str(template_path),
                        template_name=data.get('template_name', 'Мем'),
                        text_blocks=[]
                    )
                    await state.set_state(MemeCreation.entering_text)
                    await message.answer(
                        "✏️ <b>Введите текст для мема</b>\n\n"
                        "Отправьте текст который будет на меме.",
                        parse_mode="HTML"
                    )
                else:
                    await message.answer("❌ Шаблон не найден")
            
        elif action == 'create_sticker_pack':
            # User wants to create sticker pack
            name = data.get('name', '')
            title = data.get('title', 'Стикерпак')
            stickers = data.get('stickers', [])  # filenames from catalog
            custom_stickers = data.get('custom_stickers', [])  # base64 images
            
            total_stickers = len(stickers) + len(custom_stickers)
            if not name or total_stickers == 0:
                await message.answer("❌ Укажите название и выберите стикеры")
                return
            
            await message.answer("⏳ Создаю стикерпак...")
            
            try:
                # Collect all sticker files (existing + custom)
                sticker_files = []
                temp_files = []
                
                # Add existing stickers from catalog
                for filename in stickers[:50]:
                    file_path = UPLOADS_DIR / filename
                    if file_path.exists():
                        sticker_files.append(file_path)
                
                # Add custom uploaded stickers (base64)
                for b64_data in custom_stickers[:50 - len(sticker_files)]:
                    try:
                        img_data = base64.b64decode(b64_data)
                        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.png')
                        temp_file.write(img_data)
                        temp_file.close()
                        sticker_files.append(Path(temp_file.name))
                        temp_files.append(temp_file.name)
                    except Exception as e:
                        logger.warning(f"Could not decode custom sticker: {e}")
                
                if not sticker_files:
                    await message.answer("❌ Не найдены файлы стикеров")
                    return
                
                # First sticker to create pack
                first_sticker = InputSticker(
                    sticker=FSInputFile(sticker_files[0]),
                    emoji_list=["😂"],
                    format="static"
                )
                
                await bot.create_new_sticker_set(
                    user_id=message.from_user.id,
                    name=name,
                    title=title,
                    stickers=[first_sticker]
                )
                
                # Add remaining stickers
                for file_path in sticker_files[1:]:
                    try:
                        sticker = InputSticker(
                            sticker=FSInputFile(file_path),
                            emoji_list=["😂"],
                            format="static"
                        )
                        await bot.add_sticker_to_set(
                            user_id=message.from_user.id,
                            name=name,
                            sticker=sticker
                        )
                    except Exception as e:
                        logger.warning(f"Could not add sticker: {e}")
                
                # Cleanup temp files
                for temp_path in temp_files:
                    try:
                        Path(temp_path).unlink()
                    except:
                        pass
                
                await message.answer(
                    f"✅ <b>Стикерпак создан!</b>\n\n"
                    f"🎨 {title}\n"
                    f"📦 {len(sticker_files)} стикеров\n\n"
                    f"👉 t.me/addstickers/{name}",
                    parse_mode="HTML"
                )
                
            except Exception as e:
                logger.error(f"Sticker pack error: {e}")
                await message.answer(f"❌ Ошибка создания стикерпака: {str(e)[:100]}")
                
    except Exception as e:
        logger.error(f"Web app data error: {e}")
        await message.answer("❌ Ошибка обработки данных")


# ═══════════════════════════════════════════════
# COMMANDS
# ═══════════════════════════════════════════════

@router.message(Command("start"))
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    lang = detect_language(message.from_user.language_code)
    await message.answer(
        get_text("welcome", lang),
        reply_markup=main_menu_kb(lang),
        parse_mode="HTML"
    )


@router.message(Command("help"))
async def cmd_help(message: Message, state: FSMContext):
    await state.clear()
    lang = detect_language(message.from_user.language_code)
    await message.answer(
        get_text("help", lang),
        reply_markup=main_menu_kb(lang),
        parse_mode="HTML"
    )


@router.message(Command("create"))
async def cmd_create(message: Message, state: FSMContext):
    lang = detect_language(message.from_user.language_code)
    await show_template_carousel(message, state, lang, index=0)


# ═══════════════════════════════════════════════
# MAIN MENU
# ═══════════════════════════════════════════════

@router.callback_query(F.data == "main_menu")
async def cb_main_menu(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    lang = detect_language(callback.from_user.language_code)
    try:
        await callback.message.delete()
    except Exception:
        pass
    await callback.message.answer(
        get_text("welcome", lang),
        reply_markup=main_menu_kb(lang),
        parse_mode="HTML"
    )
    await callback.answer()


@router.callback_query(F.data == "help")
async def cb_help(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    lang = detect_language(callback.from_user.language_code)
    try:
        await callback.message.delete()
    except Exception:
        pass
    await callback.message.answer(
        get_text("help", lang),
        reply_markup=main_menu_kb(lang),
        parse_mode="HTML"
    )
    await callback.answer()


@router.callback_query(F.data == "open_web")
async def cb_open_web(callback: CallbackQuery):
    """Send web platform info."""
    from config import WEB_URL
    
    text = (
        "🌐 <b>Веб-платформа MemePlatform</b>\n\n"
        "Веб-интерфейс работает на твоём компьютере.\n\n"
        f"🔗 Ссылка: {WEB_URL}\n\n"
        "📱 <b>Для доступа с телефона:</b>\n"
        "1. Узнай IP компьютера в настройках Wi-Fi\n"
        "2. Открой http://[IP]:8000 на телефоне\n"
        "3. Телефон должен быть в той же сети Wi-Fi\n\n"
        "💡 Для публичного доступа используй ngrok или хостинг"
    )
    await callback.message.answer(text, parse_mode="HTML")
    await callback.answer()


@router.callback_query(F.data == "create_meme")
async def cb_create_meme(callback: CallbackQuery, state: FSMContext):
    lang = detect_language(callback.from_user.language_code)
    try:
        await callback.message.delete()
    except Exception:
        pass
    await show_template_carousel(callback.message, state, lang, index=0)
    await callback.answer()


@router.callback_query(F.data == "cancel")
async def cb_cancel(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    lang = detect_language(callback.from_user.language_code)
    try:
        await callback.message.delete()
    except Exception:
        pass
    await callback.message.answer(
        get_text("cancelled", lang),
        reply_markup=main_menu_kb(lang),
        parse_mode="HTML"
    )
    await callback.answer()


@router.callback_query(F.data == "noop")
async def cb_noop(callback: CallbackQuery):
    await callback.answer()


# ═══════════════════════════════════════════════
# TEMPLATE CAROUSEL
# ═══════════════════════════════════════════════

@router.callback_query(F.data.startswith("tpl_nav:"))
async def cb_template_navigate(callback: CallbackQuery, state: FSMContext):
    try:
        index = int(callback.data.split(":")[1])
    except (ValueError, IndexError):
        await callback.answer()
        return
    
    lang = detect_language(callback.from_user.language_code)
    templates = await get_active_templates()
    
    if not templates:
        await callback.answer(get_text("no_templates", lang), show_alert=True)
        return
    
    index = index % len(templates)
    template = templates[index]
    template_path = TEMPLATES_DIR / template["filename"]
    
    if not template_path.exists():
        await callback.answer(get_text("error_generic", lang), show_alert=True)
        return
    
    await state.update_data(carousel_index=index)
    await state.set_state(MemeCreation.selecting_template)
    
    try:
        from aiogram.types import InputMediaPhoto
        await callback.message.edit_media(
            media=InputMediaPhoto(media=FSInputFile(template_path)),
            reply_markup=template_carousel_kb(
                template_id=template["id"],
                template_name=template["name"],
                current_index=index,
                total_count=len(templates),
                lang=lang
            )
        )
    except Exception:
        try:
            await callback.message.delete()
        except Exception:
            pass
        await callback.message.answer_photo(
            photo=FSInputFile(template_path),
            reply_markup=template_carousel_kb(
                template_id=template["id"],
                template_name=template["name"],
                current_index=index,
                total_count=len(templates),
                lang=lang
            )
        )
    
    await callback.answer()


@router.callback_query(F.data.startswith("select_tpl:"))
async def cb_select_template(callback: CallbackQuery, state: FSMContext):
    try:
        template_id = int(callback.data.split(":")[1])
    except (ValueError, IndexError):
        await callback.answer()
        return
    
    lang = detect_language(callback.from_user.language_code)
    template = await get_template_by_id(template_id)
    
    if not template:
        await callback.answer(get_text("error_generic", lang), show_alert=True)
        return
    
    template_path = TEMPLATES_DIR / template["filename"]
    if not template_path.exists():
        await callback.answer(get_text("error_generic", lang), show_alert=True)
        return
    
    await state.update_data(
        template_id=template_id,
        template_path=str(template_path),
        template_name=template["name"],
        text_blocks=[],
        current_text_num=1
    )
    await state.set_state(MemeCreation.entering_text)
    
    try:
        await callback.message.delete()
    except Exception:
        pass
    
    await callback.message.answer(
        get_text("enter_text_num", lang, num=1),
        reply_markup=text_input_kb(lang, show_skip=False),
        parse_mode="HTML"
    )
    await callback.answer()


@router.callback_query(F.data == "upload_custom")
async def cb_upload_custom(callback: CallbackQuery, state: FSMContext):
    lang = detect_language(callback.from_user.language_code)
    await state.set_state(MemeCreation.uploading_image)
    try:
        await callback.message.delete()
    except Exception:
        pass
    await callback.message.answer(
        get_text("upload_image", lang),
        reply_markup=cancel_kb(lang),
        parse_mode="HTML"
    )
    await callback.answer()


# ═══════════════════════════════════════════════
# TEXT + POSITION + SIZE FLOW
# ═══════════════════════════════════════════════

@router.message(MemeCreation.entering_text, F.text)
async def handle_text_input(message: Message, state: FSMContext):
    lang = detect_language(message.from_user.language_code)
    text = message.text.strip()
    
    if len(text) > MAX_TEXT_LENGTH:
        await message.answer(
            get_text("error_text_too_long", lang, max=MAX_TEXT_LENGTH),
            reply_markup=text_input_kb(lang, show_skip=False),
            parse_mode="HTML"
        )
        return
    
    await state.update_data(current_text=text)
    await state.set_state(MemeCreation.choosing_position)
    
    await message.answer(
        get_text("choose_position_8", lang),
        reply_markup=position_kb(lang),
        parse_mode="HTML"
    )


@router.callback_query(F.data.startswith("pos:"), MemeCreation.choosing_position)
async def cb_position_selected(callback: CallbackQuery, state: FSMContext):
    lang = detect_language(callback.from_user.language_code)
    
    position = callback.data.split(":")[1]
    await state.update_data(current_position=position)
    await state.set_state(MemeCreation.choosing_font_size)
    
    await callback.message.edit_text(
        get_text("choose_font_size_simple", lang),
        reply_markup=font_size_kb(lang),
        parse_mode="HTML"
    )
    await callback.answer()


@router.callback_query(F.data.startswith("fontsize:"), MemeCreation.choosing_font_size)
async def cb_font_size_selected(callback: CallbackQuery, state: FSMContext):
    lang = detect_language(callback.from_user.language_code)
    data = await state.get_data()
    
    font_size = callback.data.split(":")[1]
    
    text_blocks = data.get("text_blocks", [])
    text_blocks.append({
        "text": data.get("current_text", ""),
        "position": data.get("current_position", "top_center"),
        "font_size": font_size
    })
    
    current_num = data.get("current_text_num", 1)
    
    await state.update_data(
        text_blocks=text_blocks,
        current_text_num=current_num + 1,
        current_text=None,
        current_position=None
    )
    await state.set_state(MemeCreation.confirm_more)
    
    await callback.message.edit_text(
        get_text("text_added", lang, num=current_num),
        reply_markup=add_more_text_kb(lang),
        parse_mode="HTML"
    )
    await callback.answer()


@router.callback_query(F.data.startswith("add_more:"), MemeCreation.confirm_more)
async def cb_add_more(callback: CallbackQuery, state: FSMContext):
    lang = detect_language(callback.from_user.language_code)
    data = await state.get_data()
    
    choice = callback.data.split(":")[1]
    
    if choice == "yes":
        current_num = data.get("current_text_num", 2)
        await state.set_state(MemeCreation.entering_text)
        
        await callback.message.edit_text(
            get_text("enter_text_num", lang, num=current_num),
            reply_markup=text_input_kb(lang, show_skip=False),
            parse_mode="HTML"
        )
    else:
        try:
            await callback.message.delete()
        except Exception:
            pass
        await generate_and_send(callback.message, state, callback.from_user)
    
    await callback.answer()


# ═══════════════════════════════════════════════
# IMAGE UPLOAD
# ═══════════════════════════════════════════════

@router.message(MemeCreation.uploading_image, F.photo)
async def handle_uploaded_photo(message: Message, state: FSMContext):
    lang = detect_language(message.from_user.language_code)
    
    photo = message.photo[-1]
    file = await message.bot.get_file(photo.file_id)
    
    UPLOADS_DIR.mkdir(parents=True, exist_ok=True)
    file_path = UPLOADS_DIR / f"upload_{message.from_user.id}_{photo.file_unique_id}.jpg"
    
    await message.bot.download_file(file.file_path, file_path)
    
    await state.update_data(
        template_id=0,
        template_path=str(file_path),
        template_name="Custom",
        text_blocks=[],
        current_text_num=1
    )
    await state.set_state(MemeCreation.entering_text)
    
    await message.answer(
        get_text("image_received", lang) + "\n\n" + get_text("enter_text_num", lang, num=1),
        reply_markup=text_input_kb(lang, show_skip=False),
        parse_mode="HTML"
    )


@router.message(MemeCreation.uploading_image)
async def handle_invalid_upload(message: Message, state: FSMContext):
    lang = detect_language(message.from_user.language_code)
    await message.answer(
        get_text("error_invalid_image", lang),
        reply_markup=cancel_kb(lang),
        parse_mode="HTML"
    )


# ═══════════════════════════════════════════════
# USER UPLOAD TO CATALOG
# ═══════════════════════════════════════════════

@router.callback_query(F.data == "add_to_catalog")
async def cb_add_to_catalog(callback: CallbackQuery, state: FSMContext):
    lang = detect_language(callback.from_user.language_code)
    
    uploads_today = await get_user_uploads_today(callback.from_user.id)
    if uploads_today >= MAX_UPLOADS_PER_DAY:
        await callback.answer(
            get_text("upload_limit_reached", lang, count=uploads_today, max=MAX_UPLOADS_PER_DAY),
            show_alert=True
        )
        return
    
    await state.set_state(MemeUpload.waiting_image)
    try:
        await callback.message.delete()
    except Exception:
        pass
    await callback.message.answer(
        get_text("upload_to_catalog", lang),
        reply_markup=cancel_kb(lang),
        parse_mode="HTML"
    )
    await callback.answer()


@router.message(MemeUpload.waiting_image, F.photo)
async def handle_catalog_upload_photo(message: Message, state: FSMContext):
    from PIL import Image
    
    lang = detect_language(message.from_user.language_code)
    photo = message.photo[-1]
    
    file = await message.bot.get_file(photo.file_id)
    
    TEMPLATES_DIR.mkdir(parents=True, exist_ok=True)
    temp_filename = f"user_{message.from_user.id}_{photo.file_unique_id}.jpg"
    file_path = TEMPLATES_DIR / temp_filename
    
    await message.bot.download_file(file.file_path, file_path)
    
    try:
        with Image.open(file_path) as img:
            width, height = img.size
            if width < MIN_IMAGE_SIZE[0] or height < MIN_IMAGE_SIZE[1]:
                file_path.unlink()
                await message.answer(
                    get_text("upload_image_too_small", lang),
                    reply_markup=cancel_kb(lang),
                    parse_mode="HTML"
                )
                return
    except Exception:
        file_path.unlink()
        await message.answer(
            get_text("error_invalid_image", lang),
            reply_markup=cancel_kb(lang),
            parse_mode="HTML"
        )
        return
    
    await state.update_data(
        upload_file_path=str(file_path),
        upload_filename=temp_filename
    )
    await state.set_state(MemeUpload.waiting_name)
    
    await message.answer(
        get_text("upload_enter_name", lang),
        reply_markup=upload_name_kb(lang),
        parse_mode="HTML"
    )


@router.message(MemeUpload.waiting_image)
async def handle_catalog_upload_invalid(message: Message, state: FSMContext):
    lang = detect_language(message.from_user.language_code)
    await message.answer(
        get_text("error_invalid_image", lang),
        reply_markup=cancel_kb(lang),
        parse_mode="HTML"
    )


@router.message(MemeUpload.waiting_name, F.text)
async def handle_catalog_upload_name(message: Message, state: FSMContext):
    lang = detect_language(message.from_user.language_code)
    name = message.text.strip()
    
    if len(name) < 2:
        await message.answer(
            get_text("upload_name_too_short", lang),
            reply_markup=upload_name_kb(lang),
            parse_mode="HTML"
        )
        return
    
    if len(name) > 50:
        await message.answer(
            get_text("upload_name_too_long", lang),
            reply_markup=upload_name_kb(lang),
            parse_mode="HTML"
        )
        return
    
    data = await state.get_data()
    filename = data.get("upload_filename")
    
    if not filename:
        await state.clear()
        await message.answer(
            get_text("error_generic", lang),
            reply_markup=main_menu_kb(lang),
            parse_mode="HTML"
        )
        return
    
    await add_user_template(name, filename, message.from_user.id)
    await increment_user_uploads(message.from_user.id)
    
    await state.clear()
    
    await message.answer(
        get_text("upload_pending_moderation", lang),
        reply_markup=main_menu_kb(lang),
        parse_mode="HTML"
    )


# ═══════════════════════════════════════════════
# HELPERS
# ═══════════════════════════════════════════════

async def show_template_carousel(message: Message, state: FSMContext, lang: str, index: int = 0):
    templates = await get_active_templates()
    
    if not templates:
        await message.answer(
            get_text("no_templates", lang),
            reply_markup=main_menu_kb(lang),
            parse_mode="HTML"
        )
        return
    
    index = index % len(templates)
    template = templates[index]
    template_path = TEMPLATES_DIR / template["filename"]
    
    if not template_path.exists():
        await message.answer(
            get_text("error_generic", lang),
            reply_markup=main_menu_kb(lang),
            parse_mode="HTML"
        )
        return
    
    await state.update_data(carousel_index=index)
    await state.set_state(MemeCreation.selecting_template)
    
    await message.answer_photo(
        photo=FSInputFile(template_path),
        reply_markup=template_carousel_kb(
            template_id=template["id"],
            template_name=template["name"],
            current_index=index,
            total_count=len(templates),
            lang=lang
        )
    )


async def generate_and_send(message: Message, state: FSMContext, user):
    lang = detect_language(user.language_code)
    data = await state.get_data()
    
    template_path = Path(data.get("template_path", ""))
    text_blocks_data = data.get("text_blocks", [])
    template_id = data.get("template_id", 0)
    
    if not template_path.exists():
        await message.answer(
            get_text("error_generic", lang),
            reply_markup=main_menu_kb(lang),
            parse_mode="HTML"
        )
        await state.clear()
        return
    
    if not text_blocks_data:
        await message.answer(
            get_text("no_text_warning", lang),
            reply_markup=main_menu_kb(lang),
            parse_mode="HTML"
        )
        await state.clear()
        return
    
    status_msg = await message.answer(
        get_text("generating", lang),
        parse_mode="HTML"
    )
    
    try:
        text_blocks = [
            TextBlock(
                text=tb["text"],
                position=tb["position"],
                font_size=tb["font_size"]
            )
            for tb in text_blocks_data
        ]
        
        meme_path = generate_meme(template_path, text_blocks)
        
        all_text = " | ".join(tb["text"] for tb in text_blocks_data)
        await save_meme(user.id, template_id, all_text, "")
        
        if template_id:
            await increment_template_usage(template_id)
        
        try:
            await status_msg.delete()
        except Exception:
            pass
        
        await message.answer_photo(
            photo=FSInputFile(meme_path),
            reply_markup=result_kb(lang)
        )
        
        logger.info(f"Meme generated for user {user.id} with {len(text_blocks)} text blocks")
        
    except Exception as e:
        logger.exception(f"Error generating meme: {e}")
        try:
            await status_msg.delete()
        except Exception:
            pass
        
        await message.answer(
            get_text("error_generic", lang),
            reply_markup=main_menu_kb(lang),
            parse_mode="HTML"
        )
    
    await state.clear()
