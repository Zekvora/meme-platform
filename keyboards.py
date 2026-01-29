"""
MemeMakerBot - Keyboard Builders
Visual template selection with photo carousel
"""
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
from aiogram.utils.keyboard import InlineKeyboardBuilder

from locales import get_text


# ═══════════════════════════════════════════════
# MAIN MENU
# ═══════════════════════════════════════════════

def main_menu_kb(lang: str = "ru") -> InlineKeyboardMarkup:
    """Main menu keyboard."""
    from config import WEB_URL
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(
            text=get_text("btn_create", lang),
            callback_data="create_meme"
        )
    )
    builder.row(
        InlineKeyboardButton(
            text=get_text("btn_add_to_catalog", lang),
            callback_data="add_to_catalog"
        )
    )
    builder.row(
        InlineKeyboardButton(
            text="� Открыть каталог",
            web_app=WebAppInfo(url=f"{WEB_URL}/miniapp")
        )
    )
    builder.row(
        InlineKeyboardButton(
            text=get_text("btn_help", lang),
            callback_data="help"
        )
    )
    return builder.as_markup()


# ═══════════════════════════════════════════════
# TEMPLATE CAROUSEL (VISUAL SELECTION)
# ═══════════════════════════════════════════════

def template_carousel_kb(
    template_id: int,
    template_name: str,
    current_index: int,
    total_count: int,
    lang: str = "ru"
) -> InlineKeyboardMarkup:
    """
    Keyboard for visual template carousel.
    Shows one template at a time with navigation.
    """
    builder = InlineKeyboardBuilder()
    
    # Row 1: Navigation arrows + counter
    nav_buttons = []
    
    # Previous button
    if current_index > 0:
        nav_buttons.append(InlineKeyboardButton(
            text="◀️",
            callback_data=f"tpl_nav:{current_index - 1}"
        ))
    else:
        nav_buttons.append(InlineKeyboardButton(
            text="◀️",
            callback_data=f"tpl_nav:{total_count - 1}"  # Loop to end
        ))
    
    # Counter
    nav_buttons.append(InlineKeyboardButton(
        text=f"{current_index + 1}/{total_count}",
        callback_data="noop"
    ))
    
    # Next button
    if current_index < total_count - 1:
        nav_buttons.append(InlineKeyboardButton(
            text="▶️",
            callback_data=f"tpl_nav:{current_index + 1}"
        ))
    else:
        nav_buttons.append(InlineKeyboardButton(
            text="▶️",
            callback_data="tpl_nav:0"  # Loop to start
        ))
    
    builder.row(*nav_buttons)
    
    # Row 2: Select this template
    builder.row(
        InlineKeyboardButton(
            text=f"✅ {get_text('btn_select', lang)}",
            callback_data=f"select_tpl:{template_id}"
        )
    )
    
    # Row 3: Upload custom
    builder.row(
        InlineKeyboardButton(
            text=get_text("btn_upload", lang),
            callback_data="upload_custom"
        )
    )
    
    # Row 4: Cancel
    builder.row(
        InlineKeyboardButton(
            text=get_text("btn_cancel", lang),
            callback_data="cancel"
        )
    )
    
    return builder.as_markup()


# ═══════════════════════════════════════════════
# FONT SIZE (SIMPLE)
# ═══════════════════════════════════════════════

def font_size_kb(lang: str = "ru") -> InlineKeyboardMarkup:
    """Simple font size selection."""
    builder = InlineKeyboardBuilder()
    
    builder.row(
        InlineKeyboardButton(text="🔹 S", callback_data="fontsize:small"),
        InlineKeyboardButton(text="🔸 M", callback_data="fontsize:medium"),
        InlineKeyboardButton(text="🔶 L", callback_data="fontsize:large")
    )
    builder.row(
        InlineKeyboardButton(
            text=get_text("btn_auto_size", lang),
            callback_data="fontsize:auto"
        )
    )
    builder.row(
        InlineKeyboardButton(
            text=get_text("btn_cancel", lang),
            callback_data="cancel"
        )
    )
    
    return builder.as_markup()


# ═══════════════════════════════════════════════
# 10 POSITIONS (4 left, 4 right, top, bottom)
# ═══════════════════════════════════════════════

def position_kb(lang: str = "ru") -> InlineKeyboardMarkup:
    """10 position selection: 4 left, 4 right, top center, bottom center."""
    builder = InlineKeyboardBuilder()
    
    # Top center
    builder.row(
        InlineKeyboardButton(text="⬆️ Сверху", callback_data="pos:top")
    )
    
    # 4 rows: left and right
    builder.row(
        InlineKeyboardButton(text="⬅️ 1", callback_data="pos:left_1"),
        InlineKeyboardButton(text="1 ➡️", callback_data="pos:right_1")
    )
    builder.row(
        InlineKeyboardButton(text="⬅️ 2", callback_data="pos:left_2"),
        InlineKeyboardButton(text="2 ➡️", callback_data="pos:right_2")
    )
    builder.row(
        InlineKeyboardButton(text="⬅️ 3", callback_data="pos:left_3"),
        InlineKeyboardButton(text="3 ➡️", callback_data="pos:right_3")
    )
    builder.row(
        InlineKeyboardButton(text="⬅️ 4", callback_data="pos:left_4"),
        InlineKeyboardButton(text="4 ➡️", callback_data="pos:right_4")
    )
    
    # Bottom center
    builder.row(
        InlineKeyboardButton(text="⬇️ Снизу", callback_data="pos:bottom")
    )
    
    builder.row(
        InlineKeyboardButton(
            text=get_text("btn_cancel", lang),
            callback_data="cancel"
        )
    )
    
    return builder.as_markup()


def add_more_text_kb(lang: str = "ru") -> InlineKeyboardMarkup:
    """Add more text or generate meme."""
    builder = InlineKeyboardBuilder()
    
    builder.row(
        InlineKeyboardButton(
            text=get_text("btn_add_text", lang),
            callback_data="add_more:yes"
        )
    )
    builder.row(
        InlineKeyboardButton(
            text=get_text("btn_generate_now", lang),
            callback_data="add_more:no"
        )
    )
    builder.row(
        InlineKeyboardButton(
            text=get_text("btn_cancel", lang),
            callback_data="cancel"
        )
    )
    
    return builder.as_markup()


# ═══════════════════════════════════════════════
# TEXT INPUT
# ═══════════════════════════════════════════════

def text_input_kb(lang: str = "ru", show_skip: bool = True) -> InlineKeyboardMarkup:
    """Text input keyboard with skip/cancel."""
    builder = InlineKeyboardBuilder()
    
    if show_skip:
        builder.row(
            InlineKeyboardButton(
                text=get_text("btn_skip", lang),
                callback_data="skip_text"
            )
        )
    
    builder.row(
        InlineKeyboardButton(
            text=get_text("btn_cancel", lang),
            callback_data="cancel"
        )
    )
    
    return builder.as_markup()


def result_kb(lang: str = "ru") -> InlineKeyboardMarkup:
    """Result keyboard after meme generation."""
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(
            text=get_text("btn_again", lang),
            callback_data="create_meme"
        )
    )
    builder.row(
        InlineKeyboardButton(
            text=get_text("btn_back", lang),
            callback_data="main_menu"
        )
    )
    return builder.as_markup()


def cancel_kb(lang: str = "ru") -> InlineKeyboardMarkup:
    """Cancel only keyboard."""
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(
            text=get_text("btn_cancel", lang),
            callback_data="cancel"
        )
    )
    return builder.as_markup()


# ═══════════════════════════════════════════════
# ADMIN KEYBOARDS
# ═══════════════════════════════════════════════

def admin_menu_kb(lang: str = "ru", pending_count: int = 0) -> InlineKeyboardMarkup:
    """Admin main menu."""
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(
            text=get_text("btn_admin_stats", lang),
            callback_data="admin:stats"
        ),
        InlineKeyboardButton(
            text=get_text("btn_admin_templates", lang),
            callback_data="admin:templates"
        )
    )
    # Moderation button with pending count
    mod_text = get_text("btn_admin_moderation", lang, count=pending_count)
    builder.row(
        InlineKeyboardButton(
            text=mod_text,
            callback_data="admin:moderation"
        )
    )
    builder.row(
        InlineKeyboardButton(
            text=get_text("btn_admin_broadcast", lang),
            callback_data="admin:broadcast"
        ),
        InlineKeyboardButton(
            text=get_text("btn_admin_settings", lang),
            callback_data="admin:settings"
        )
    )
    builder.row(
        InlineKeyboardButton(
            text=get_text("btn_back", lang),
            callback_data="main_menu"
        )
    )
    return builder.as_markup()


def admin_templates_kb(templates: list[dict], lang: str = "ru") -> InlineKeyboardMarkup:
    """Admin templates management."""
    builder = InlineKeyboardBuilder()
    
    for t in templates[:10]:
        status = "✅" if t.get("is_active", 1) else "❌"
        builder.row(
            InlineKeyboardButton(
                text=f"{status} {t['name'][:15]}",
                callback_data=f"admin:tmpl_toggle:{t['id']}"
            ),
            InlineKeyboardButton(
                text="🗑",
                callback_data=f"admin:tmpl_delete:{t['id']}"
            )
        )
    
    builder.row(
        InlineKeyboardButton(
            text=get_text("btn_admin_add_template", lang),
            callback_data="admin:tmpl_add"
        )
    )
    builder.row(
        InlineKeyboardButton(
            text=get_text("btn_admin_back", lang),
            callback_data="admin:menu"
        )
    )
    
    return builder.as_markup()


def admin_broadcast_confirm_kb(lang: str = "ru") -> InlineKeyboardMarkup:
    """Broadcast confirmation."""
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(
            text=get_text("btn_confirm", lang),
            callback_data="admin:broadcast_confirm"
        ),
        InlineKeyboardButton(
            text=get_text("btn_cancel", lang),
            callback_data="admin:broadcast_cancel"
        )
    )
    return builder.as_markup()


def back_to_admin_kb(lang: str = "ru") -> InlineKeyboardMarkup:
    """Back to admin menu."""
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(
            text=get_text("btn_admin_back", lang),
            callback_data="admin:menu"
        )
    )
    return builder.as_markup()


def moderation_kb(template_id: int, lang: str = "ru") -> InlineKeyboardMarkup:
    """Moderation keyboard for pending templates."""
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(
            text=get_text("btn_approve", lang),
            callback_data=f"mod:approve:{template_id}"
        ),
        InlineKeyboardButton(
            text=get_text("btn_reject", lang),
            callback_data=f"mod:reject:{template_id}"
        )
    )
    builder.row(
        InlineKeyboardButton(
            text=get_text("btn_admin_back", lang),
            callback_data="admin:moderation"
        )
    )
    return builder.as_markup()


def upload_name_kb(lang: str = "ru") -> InlineKeyboardMarkup:
    """Keyboard for upload name input."""
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(
            text=get_text("btn_cancel", lang),
            callback_data="cancel"
        )
    )
    return builder.as_markup()
