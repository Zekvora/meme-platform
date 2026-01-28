"""
MemeMakerBot - FSM States
8-position text placement flow
"""
from aiogram.fsm.state import State, StatesGroup


class MemeCreation(StatesGroup):
    """Meme creation with 8 text positions."""
    selecting_template = State()
    uploading_image = State()
    entering_text = State()       # Ввод текста
    choosing_position = State()   # Выбор из 8 позиций
    choosing_font_size = State()  # Размер шрифта
    confirm_more = State()        # Добавить ещё?


class MemeUpload(StatesGroup):
    """User meme upload flow."""
    waiting_image = State()
    waiting_name = State()


class AdminStates(StatesGroup):
    """Admin panel states."""
    adding_template = State()
    broadcast_message = State()
    broadcast_confirm = State()
    moderating = State()
