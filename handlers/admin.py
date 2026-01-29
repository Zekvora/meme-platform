"""
MemeMakerBot - Admin Handlers (Fully Working)
Complete admin panel with all buttons functional
"""
import logging
import asyncio

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, FSInputFile, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from config import ADMIN_IDS, TEMPLATES_DIR, RATE_LIMIT, RATE_PERIOD, MAX_TEXT_LENGTH, TEMPLATES_PER_PAGE
from database import (
    get_users_count, get_memes_count, get_errors_count,
    get_active_templates, toggle_template, delete_template,
    add_template, get_all_user_ids, get_templates_count,
    get_all_templates, get_pending_templates, approve_template,
    reject_template, get_pending_count
)
import database_new as db_new
from keyboards import (
    admin_menu_kb, admin_templates_kb, 
    admin_broadcast_confirm_kb, back_to_admin_kb, cancel_kb,
    moderation_kb
)
from locales import get_text, detect_language
from states import AdminStates

logger = logging.getLogger(__name__)
router = Router()


def is_admin(user_id: int) -> bool:
    """Check if user is admin."""
    return user_id in ADMIN_IDS


# ═══════════════════════════════════════════════
# ADMIN COMMAND
# ═══════════════════════════════════════════════

@router.message(Command("admin"))
async def cmd_admin(message: Message, state: FSMContext):
    """Admin panel entry point."""
    if not is_admin(message.from_user.id):
        return  # Silent fail
    
    await state.clear()
    lang = detect_language(message.from_user.language_code)
    
    users = await get_users_count()
    memes = await get_memes_count()
    errors = await get_errors_count()
    pending = await get_pending_count()
    
    await message.answer(
        get_text("admin_welcome", lang, users=users, memes=memes, errors=errors),
        reply_markup=admin_menu_kb(lang, pending_count=pending),
        parse_mode="HTML"
    )


@router.message(Command("weblogin"))
async def cmd_weblogin(message: Message):
    """Generate one-time code for web admin panel login."""
    if not is_admin(message.from_user.id):
        return  # Silent fail
    
    lang = detect_language(message.from_user.language_code)
    
    # Generate code
    code = await db_new.generate_admin_code(message.from_user.id)
    tg_id = message.from_user.id
    
    # Build login URL
    login_url = f"https://web-production-9a1f5.up.railway.app/login?token={code}&tg={tg_id}"
    
    # Send link
    text = (
        "🔐 <b>Вход в веб-панель</b>\n\n"
        f"Нажмите кнопку ниже для входа:\n\n"
        "⏱ Ссылка действительна 10 минут\n"
        "⚠️ Не передавайте ссылку третьим лицам!"
    )
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔓 Войти в панель", url=login_url)]
    ])
    
    await message.answer(text, parse_mode="HTML", reply_markup=keyboard)


# ═══════════════════════════════════════════════
# ADMIN MENU CALLBACKS
# ═══════════════════════════════════════════════

@router.callback_query(F.data == "admin:menu")
async def cb_admin_menu(callback: CallbackQuery, state: FSMContext):
    """Return to admin menu."""
    if not is_admin(callback.from_user.id):
        await callback.answer(get_text("admin_access_denied", "ru"), show_alert=True)
        return
    
    await state.clear()
    lang = detect_language(callback.from_user.language_code)
    
    users = await get_users_count()
    memes = await get_memes_count()
    errors = await get_errors_count()
    pending = await get_pending_count()
    
    # Handle photo message (from moderation)
    try:
        await callback.message.delete()
    except Exception:
        pass
    
    await callback.message.answer(
        get_text("admin_welcome", lang, users=users, memes=memes, errors=errors),
        reply_markup=admin_menu_kb(lang, pending_count=pending),
        parse_mode="HTML"
    )
    await callback.answer()


@router.callback_query(F.data == "admin:stats")
async def cb_admin_stats(callback: CallbackQuery, state: FSMContext):
    """Show detailed statistics."""
    if not is_admin(callback.from_user.id):
        await callback.answer(get_text("admin_access_denied", "ru"), show_alert=True)
        return
    
    await state.clear()
    lang = detect_language(callback.from_user.language_code)
    
    users = await get_users_count()
    memes = await get_memes_count()
    errors = await get_errors_count()
    templates = await get_templates_count()
    
    await callback.message.edit_text(
        get_text("admin_stats", lang, users=users, memes=memes, templates=templates, errors=errors),
        reply_markup=back_to_admin_kb(lang),
        parse_mode="HTML"
    )
    await callback.answer()


# ═══════════════════════════════════════════════
# TEMPLATES MANAGEMENT
# ═══════════════════════════════════════════════

@router.callback_query(F.data == "admin:templates")
async def cb_admin_templates(callback: CallbackQuery, state: FSMContext):
    """Show templates management."""
    if not is_admin(callback.from_user.id):
        await callback.answer(get_text("admin_access_denied", "ru"), show_alert=True)
        return
    
    await state.clear()
    lang = detect_language(callback.from_user.language_code)
    
    all_templates = await get_all_templates()
    
    await callback.message.edit_text(
        get_text("admin_templates", lang, count=len(all_templates)),
        reply_markup=admin_templates_kb(all_templates, lang),
        parse_mode="HTML"
    )
    await callback.answer()


@router.callback_query(F.data.startswith("admin:tmpl_toggle:"))
async def cb_toggle_template(callback: CallbackQuery, state: FSMContext):
    """Toggle template active status."""
    if not is_admin(callback.from_user.id):
        await callback.answer(get_text("admin_access_denied", "ru"), show_alert=True)
        return
    
    lang = detect_language(callback.from_user.language_code)
    template_id = int(callback.data.split(":")[2])
    
    # Toggle status
    all_templates = await get_all_templates()
    current_template = next((t for t in all_templates if t["id"] == template_id), None)
    
    if current_template:
        new_status = not bool(current_template.get("is_active", 1))
        await toggle_template(template_id, new_status)
        await callback.answer(get_text("admin_template_toggled", lang))
    
    # Refresh templates list
    all_templates = await get_all_templates()
    await callback.message.edit_text(
        get_text("admin_templates", lang, count=len(all_templates)),
        reply_markup=admin_templates_kb(all_templates, lang),
        parse_mode="HTML"
    )


@router.callback_query(F.data.startswith("admin:tmpl_delete:"))
async def cb_delete_template(callback: CallbackQuery, state: FSMContext):
    """Delete template."""
    if not is_admin(callback.from_user.id):
        await callback.answer(get_text("admin_access_denied", "ru"), show_alert=True)
        return
    
    lang = detect_language(callback.from_user.language_code)
    template_id = int(callback.data.split(":")[2])
    
    await delete_template(template_id)
    await callback.answer(get_text("admin_template_deleted", lang))
    
    # Refresh templates list
    all_templates = await get_all_templates()
    await callback.message.edit_text(
        get_text("admin_templates", lang, count=len(all_templates)),
        reply_markup=admin_templates_kb(all_templates, lang),
        parse_mode="HTML"
    )


@router.callback_query(F.data == "admin:tmpl_add")
async def cb_add_template_start(callback: CallbackQuery, state: FSMContext):
    """Start adding a new template."""
    if not is_admin(callback.from_user.id):
        await callback.answer(get_text("admin_access_denied", "ru"), show_alert=True)
        return
    
    lang = detect_language(callback.from_user.language_code)
    
    await state.set_state(AdminStates.adding_template)
    
    await callback.message.edit_text(
        get_text("admin_add_template_prompt", lang),
        reply_markup=cancel_kb(lang),
        parse_mode="HTML"
    )
    await callback.answer()


@router.message(AdminStates.adding_template, F.photo)
async def handle_new_template(message: Message, state: FSMContext):
    """Handle new template upload."""
    if not is_admin(message.from_user.id):
        return
    
    lang = detect_language(message.from_user.language_code)
    
    photo = message.photo[-1]
    name = message.caption or f"Шаблон {photo.file_unique_id[:8]}"
    filename = f"template_{photo.file_unique_id}.jpg"
    
    file = await message.bot.get_file(photo.file_id)
    file_path = TEMPLATES_DIR / filename
    TEMPLATES_DIR.mkdir(parents=True, exist_ok=True)
    
    await message.bot.download_file(file.file_path, file_path)
    await add_template(name, filename)
    
    await state.clear()
    
    await message.answer(
        get_text("admin_template_added", lang, name=name),
        reply_markup=back_to_admin_kb(lang),
        parse_mode="HTML"
    )


@router.message(AdminStates.adding_template)
async def handle_invalid_template(message: Message, state: FSMContext):
    """Handle invalid template upload."""
    lang = detect_language(message.from_user.language_code)
    await message.answer(
        get_text("error_invalid_image", lang),
        reply_markup=cancel_kb(lang),
        parse_mode="HTML"
    )


# ═══════════════════════════════════════════════
# MODERATION
# ═══════════════════════════════════════════════

@router.callback_query(F.data == "admin:moderation")
async def cb_admin_moderation(callback: CallbackQuery, state: FSMContext):
    """Show pending memes for moderation."""
    if not is_admin(callback.from_user.id):
        await callback.answer(get_text("admin_access_denied", "ru"), show_alert=True)
        return
    
    lang = detect_language(callback.from_user.language_code)
    pending = await get_pending_templates()
    
    # Delete any previous message (might be photo)
    try:
        await callback.message.delete()
    except Exception:
        pass
    
    if not pending:
        await callback.message.answer(
            get_text("admin_moderation_empty", lang),
            reply_markup=back_to_admin_kb(lang),
            parse_mode="HTML"
        )
        await callback.answer()
        return
    
    # Show first pending template
    template = pending[0]
    template_path = TEMPLATES_DIR / template["filename"]
    
    if template_path.exists():
        from aiogram.types import FSInputFile
        
        await state.update_data(moderation_index=0)
        await state.set_state(AdminStates.moderating)
        
        await callback.message.answer_photo(
            photo=FSInputFile(template_path),
            caption=get_text("admin_moderation_item", lang, 
                           name=template["name"], 
                           user_id=template["uploaded_by"]),
            reply_markup=moderation_kb(template["id"], lang),
            parse_mode="HTML"
        )
    else:
        # File missing, reject automatically
        await reject_template(template["id"])
        await callback.message.answer(
            get_text("admin_moderation_title", lang, count=len(pending) - 1),
            reply_markup=back_to_admin_kb(lang),
            parse_mode="HTML"
        )
    
    await callback.answer()


@router.callback_query(F.data.startswith("mod:approve:"))
async def cb_approve_template(callback: CallbackQuery, state: FSMContext):
    """Approve pending template."""
    if not is_admin(callback.from_user.id):
        await callback.answer(get_text("admin_access_denied", "ru"), show_alert=True)
        return
    
    lang = detect_language(callback.from_user.language_code)
    template_id = int(callback.data.split(":")[2])
    
    await approve_template(template_id)
    await callback.answer(get_text("admin_approved", lang), show_alert=True)
    
    # Show next pending or return to moderation list
    pending = await get_pending_templates()
    
    try:
        await callback.message.delete()
    except Exception:
        pass
    
    if not pending:
        await callback.message.answer(
            get_text("admin_moderation_empty", lang),
            reply_markup=back_to_admin_kb(lang),
            parse_mode="HTML"
        )
        return
    
    # Show next template
    template = pending[0]
    template_path = TEMPLATES_DIR / template["filename"]
    
    if template_path.exists():
        from aiogram.types import FSInputFile
        
        await callback.message.answer_photo(
            photo=FSInputFile(template_path),
            caption=get_text("admin_moderation_item", lang, 
                           name=template["name"], 
                           user_id=template["uploaded_by"]),
            reply_markup=moderation_kb(template["id"], lang),
            parse_mode="HTML"
        )
    else:
        await reject_template(template["id"])
        # Recurse to show next
        await cb_admin_moderation(callback, state)


@router.callback_query(F.data.startswith("mod:reject:"))
async def cb_reject_template(callback: CallbackQuery, state: FSMContext):
    """Reject pending template."""
    if not is_admin(callback.from_user.id):
        await callback.answer(get_text("admin_access_denied", "ru"), show_alert=True)
        return
    
    lang = detect_language(callback.from_user.language_code)
    template_id = int(callback.data.split(":")[2])
    
    await reject_template(template_id)
    await callback.answer(get_text("admin_rejected", lang), show_alert=True)
    
    # Show next pending or return to moderation list
    pending = await get_pending_templates()
    
    try:
        await callback.message.delete()
    except Exception:
        pass
    
    if not pending:
        await callback.message.answer(
            get_text("admin_moderation_empty", lang),
            reply_markup=back_to_admin_kb(lang),
            parse_mode="HTML"
        )
        return
    
    # Show next template
    template = pending[0]
    template_path = TEMPLATES_DIR / template["filename"]
    
    if template_path.exists():
        from aiogram.types import FSInputFile
        
        await callback.message.answer_photo(
            photo=FSInputFile(template_path),
            caption=get_text("admin_moderation_item", lang, 
                           name=template["name"], 
                           user_id=template["uploaded_by"]),
            reply_markup=moderation_kb(template["id"], lang),
            parse_mode="HTML"
        )
    else:
        await reject_template(template["id"])
        # Recurse to show next
        await cb_admin_moderation(callback, state)


# ═══════════════════════════════════════════════
# BROADCAST
# ═══════════════════════════════════════════════

@router.callback_query(F.data == "admin:broadcast")
async def cb_broadcast_start(callback: CallbackQuery, state: FSMContext):
    """Start broadcast."""
    if not is_admin(callback.from_user.id):
        await callback.answer(get_text("admin_access_denied", "ru"), show_alert=True)
        return
    
    lang = detect_language(callback.from_user.language_code)
    
    await state.set_state(AdminStates.broadcast_message)
    
    await callback.message.edit_text(
        get_text("admin_broadcast", lang),
        reply_markup=cancel_kb(lang),
        parse_mode="HTML"
    )
    await callback.answer()


@router.message(AdminStates.broadcast_message)
async def handle_broadcast_message(message: Message, state: FSMContext):
    """Handle broadcast message input."""
    if not is_admin(message.from_user.id):
        return
    
    lang = detect_language(message.from_user.language_code)
    
    broadcast_text = message.text or message.caption or ""
    if not broadcast_text:
        await message.answer(
            get_text("admin_no_message", lang),
            reply_markup=cancel_kb(lang),
            parse_mode="HTML"
        )
        return
    
    users = await get_all_user_ids()
    preview = broadcast_text[:100] + "..." if len(broadcast_text) > 100 else broadcast_text
    
    await state.update_data(broadcast_text=broadcast_text)
    await state.set_state(AdminStates.broadcast_confirm)
    
    await message.answer(
        get_text("admin_broadcast_confirm", lang, count=len(users), preview=preview),
        reply_markup=admin_broadcast_confirm_kb(lang),
        parse_mode="HTML"
    )


@router.callback_query(F.data == "admin:broadcast_confirm", AdminStates.broadcast_confirm)
async def cb_broadcast_confirm(callback: CallbackQuery, state: FSMContext):
    """Confirm and send broadcast."""
    if not is_admin(callback.from_user.id):
        await callback.answer(get_text("admin_access_denied", "ru"), show_alert=True)
        return
    
    lang = detect_language(callback.from_user.language_code)
    data = await state.get_data()
    broadcast_text = data.get("broadcast_text", "")
    
    if not broadcast_text:
        await callback.answer(get_text("admin_no_message", lang), show_alert=True)
        await state.clear()
        return
    
    users = await get_all_user_ids()
    total = len(users)
    sent = 0
    
    status_msg = await callback.message.edit_text(
        get_text("admin_broadcast_sending", lang, current=0, total=total),
        parse_mode="HTML"
    )
    
    for i, user_id in enumerate(users):
        try:
            await callback.bot.send_message(user_id, broadcast_text)
            sent += 1
        except Exception as e:
            logger.warning(f"Failed to send broadcast to {user_id}: {e}")
        
        # Update progress every 10 users
        if (i + 1) % 10 == 0:
            try:
                await status_msg.edit_text(
                    get_text("admin_broadcast_sending", lang, current=i+1, total=total),
                    parse_mode="HTML"
                )
            except Exception:
                pass
        
        await asyncio.sleep(0.05)  # Rate limit
    
    await state.clear()
    
    await status_msg.edit_text(
        get_text("admin_broadcast_done", lang, sent=sent, total=total),
        reply_markup=back_to_admin_kb(lang),
        parse_mode="HTML"
    )
    await callback.answer()


@router.callback_query(F.data == "admin:broadcast_cancel")
async def cb_broadcast_cancel(callback: CallbackQuery, state: FSMContext):
    """Cancel broadcast."""
    await state.clear()
    lang = detect_language(callback.from_user.language_code)
    
    users = await get_users_count()
    memes = await get_memes_count()
    errors = await get_errors_count()
    
    await callback.message.edit_text(
        get_text("admin_welcome", lang, users=users, memes=memes, errors=errors),
        reply_markup=admin_menu_kb(lang),
        parse_mode="HTML"
    )
    await callback.answer()


# ═══════════════════════════════════════════════
# SETTINGS
# ═══════════════════════════════════════════════

@router.callback_query(F.data == "admin:settings")
async def cb_admin_settings(callback: CallbackQuery, state: FSMContext):
    """Show bot settings."""
    if not is_admin(callback.from_user.id):
        await callback.answer(get_text("admin_access_denied", "ru"), show_alert=True)
        return
    
    await state.clear()
    lang = detect_language(callback.from_user.language_code)
    
    await callback.message.edit_text(
        get_text("admin_settings", lang, 
                 rate_limit=RATE_LIMIT, 
                 rate_period=RATE_PERIOD,
                 max_text=MAX_TEXT_LENGTH,
                 per_page=TEMPLATES_PER_PAGE),
        reply_markup=back_to_admin_kb(lang),
        parse_mode="HTML"
    )
    await callback.answer()


# ═══════════════════════════════════════════════
# CANCEL FOR ADMIN STATES
# ═══════════════════════════════════════════════

@router.callback_query(F.data == "cancel", AdminStates.adding_template)
@router.callback_query(F.data == "cancel", AdminStates.broadcast_message)
@router.callback_query(F.data == "cancel", AdminStates.broadcast_confirm)
async def cb_admin_cancel(callback: CallbackQuery, state: FSMContext):
    """Cancel admin operations and return to admin menu."""
    if not is_admin(callback.from_user.id):
        await callback.answer()
        return
    
    await state.clear()
    lang = detect_language(callback.from_user.language_code)
    
    users = await get_users_count()
    memes = await get_memes_count()
    errors = await get_errors_count()
    
    await callback.message.edit_text(
        get_text("admin_welcome", lang, users=users, memes=memes, errors=errors),
        reply_markup=admin_menu_kb(lang),
        parse_mode="HTML"
    )
    await callback.answer()
