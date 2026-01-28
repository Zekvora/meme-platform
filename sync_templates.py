"""
Sync templates from bot to web database
"""
import asyncio
import shutil
from pathlib import Path

from config import TEMPLATES_DIR, UPLOADS_DIR
import database_new as db

# Шаблоны из бота
TEMPLATES = [
    ("Дрейк", "drake.jpg", "Приколы", "😂"),
    ("Парень отвлёкся", "distracted.jpg", "Приколы", "😂"),
    ("Две кнопки", "buttons.jpg", "Приколы", "😂"),
    ("Расширение мозга", "brain.jpg", "IT и программирование", "💻"),
    ("Измени моё мнение", "changemymind.jpg", "Приколы", "😂"),
    ("Нельзя просто так", "onedoesnot.jpg", "Кино и ТВ", "🎬"),
    ("Успешный малыш", "success-kid.jpg", "Жизненное", "🌍"),
    ("Неудачник Брайан", "bad-luck-brian.jpg", "Жизненное", "🌍"),
    ("Философораптор", "philosoraptor.jpg", "Приколы", "😂"),
    ("Фрай из Футурамы", "futurama-fry.jpg", "Кино и ТВ", "🎬"),
    ("Древние пришельцы", "ancient-aliens.jpg", "Кино и ТВ", "🎬"),
    ("Бэтмен даёт пощёчину", "batman-slapping.jpg", "Кино и ТВ", "🎬"),
    ("Грустный кот", "grumpy-cat.jpg", "Животные", "🐱"),
    ("Проблемы первого мира", "first-world.jpg", "Жизненное", "🌍"),
    ("Доге", "doge.jpg", "Животные", "🐱"),
    ("Это бабочка?", "is-this.jpg", "Приколы", "😂"),
    ("Умный темнокожий", "roll-safe.jpg", "Приколы", "😂"),
    ("Съезд с трассы", "left-exit.jpg", "Приколы", "😂"),
    ("Женщина и кот", "woman-yelling.jpg", "Приколы", "😂"),
    ("Всегда так было", "always-has-been.jpg", "Игры", "🎮"),
    ("Девочка-катастрофа", "disaster-girl.jpg", "Приколы", "😂"),
    ("UNO +4", "uno-draw.jpg", "Игры", "🎮"),
    ("Гарольд скрывает боль", "hide-pain-harold.jpg", "Жизненное", "🌍"),
    ("Скелет ждёт", "waiting-skeleton.jpg", "Жизненное", "🌍"),
    ("Удивлённый Пикачу", "pikachu.jpg", "Игры", "🎮"),
    ("Предложение обмена", "trade-offer.jpg", "Приколы", "😂"),
    ("План Грю", "gru-plan.jpg", "Кино и ТВ", "🎬"),
    ("Берни в варежках", "bernie-mittens.jpg", "Политика", "🏛️"),
    ("Совет директоров", "boardroom.jpg", "Жизненное", "🌍"),
    ("Это норма", "this-is-fine.jpg", "Приколы", "😂"),
    ("Грустный Пабло", "sad-pablo.jpg", "Кино и ТВ", "🎬"),
    ("Видишь? Никто", "see-nobody.jpg", "Приколы", "😂"),
    ("Паник/Калм", "panik-kalm.jpg", "Приколы", "😂"),
    ("Эпичное рукопожатие", "epic-handshake.jpg", "Приколы", "😂"),
    ("Типы головной боли", "types-headaches.jpg", "Жизненное", "🌍"),
    ("Качок Доге", "buff-doge.jpg", "Животные", "🐱"),
    ("Человеки-пауки", "spiderman-pointing.jpg", "Кино и ТВ", "🎬"),
    ("Думающий", "thinking.jpg", "Приколы", "😂"),
    ("Обезьяна-кукла", "monkey-puppet.jpg", "Животные", "🐱"),
    ("Спящий Шак", "sleeping-shaq.jpg", "Приколы", "😂"),
    ("Стонкс", "stonks.jpg", "IT и программирование", "💻"),
    ("Злой NPC", "angry-npc.jpg", "Игры", "🎮"),
    ("Макияж клоуна", "clown-makeup.jpg", "Приколы", "😂"),
    ("Я что, шутка?", "am-i-joke.jpg", "Приколы", "😂"),
]


async def sync_templates():
    """Sync templates to web database."""
    print("🚀 Syncing templates to web...")
    
    await db.init_db()
    
    # Get categories
    categories = await db.get_categories()
    cat_map = {c["name"]: c["id"] for c in categories}
    
    added = 0
    for title, filename, cat_name, icon in TEMPLATES:
        src = TEMPLATES_DIR / filename
        if not src.exists():
            print(f"❌ Missing: {filename}")
            continue
        
        # Copy to uploads
        dst = UPLOADS_DIR / filename
        if not dst.exists():
            shutil.copy(src, dst)
        
        # Get category ID
        cat_id = cat_map.get(cat_name)
        if not cat_id:
            # Create category
            cat_id = await db.create_category(cat_name, icon=icon)
            cat_map[cat_name] = cat_id
        
        # Check if meme exists
        existing = await db.get_memes(limit=1000)
        if any(m["filename"] == filename for m in existing):
            print(f"⏭ Exists: {title}")
            continue
        
        # Add meme
        await db.create_meme(
            author_id=1,  # System user
            title=title,
            description=f"Классический мем-шаблон: {title}",
            filename=filename,
            file_type="image",
            category_id=cat_id,
            status="approved"
        )
        print(f"✅ Added: {title}")
        added += 1
    
    print(f"\n🎉 Done! Added {added} memes")


if __name__ == "__main__":
    asyncio.run(sync_templates())
