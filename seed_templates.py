"""
MemeMakerBot - Template Seeder
Seeds database with 40+ real meme templates.
"""
import asyncio
from pathlib import Path

from config import TEMPLATES_DIR
from database import init_db, add_template, get_all_templates


# 40+ мем-шаблонов с русскими названиями
SEED_TEMPLATES = [
    # Классика
    ("Дрейк", "drake.jpg"),
    ("Парень отвлёкся", "distracted.jpg"),
    ("Две кнопки", "buttons.jpg"),
    ("Расширение мозга", "brain.jpg"),
    ("Измени моё мнение", "changemymind.jpg"),
    ("Нельзя просто так", "onedoesnot.jpg"),
    
    # Популярные мемы
    ("Успешный малыш", "success-kid.jpg"),
    ("Неудачник Брайан", "bad-luck-brian.jpg"),
    ("Философораптор", "philosoraptor.jpg"),
    ("Фрай из Футурамы", "futurama-fry.jpg"),
    ("Древние пришельцы", "ancient-aliens.jpg"),
    ("Бэтмен даёт пощёчину", "batman-slapping.jpg"),
    ("Грустный кот", "grumpy-cat.jpg"),
    ("Проблемы первого мира", "first-world.jpg"),
    ("Доге", "doge.jpg"),
    ("Это бабочка?", "is-this.jpg"),
    
    # Современные мемы
    ("Умный темнокожий", "roll-safe.jpg"),
    ("Съезд с трассы", "left-exit.jpg"),
    ("Женщина и кот", "woman-yelling.jpg"),
    ("Всегда так было", "always-has-been.jpg"),
    ("Девочка-катастрофа", "disaster-girl.jpg"),
    ("UNO +4", "uno-draw.jpg"),
    ("Гарольд скрывает боль", "hide-pain-harold.jpg"),
    ("Скелет ждёт", "waiting-skeleton.jpg"),
    ("Удивлённый Пикачу", "pikachu.jpg"),
    ("Предложение обмена", "trade-offer.jpg"),
    
    # Ещё популярные
    ("План Грю", "gru-plan.jpg"),
    ("Берни в варежках", "bernie-mittens.jpg"),
    ("Совет директоров", "boardroom.jpg"),
    ("Это норма", "this-is-fine.jpg"),
    ("Грустный Пабло", "sad-pablo.jpg"),
    ("Видишь? Никто", "see-nobody.jpg"),
    ("Паник/Калм", "panik-kalm.jpg"),
    ("Эпичное рукопожатие", "epic-handshake.jpg"),
    ("Типы головной боли", "types-headaches.jpg"),
    ("Качок Доге", "buff-doge.jpg"),
    
    # Дополнительные
    ("Человеки-пауки", "spiderman-pointing.jpg"),
    ("Думающий", "thinking.jpg"),
    ("Обезьяна-кукла", "monkey-puppet.jpg"),
    ("Спящий Шак", "sleeping-shaq.jpg"),
    ("Стонкс", "stonks.jpg"),
    ("Злой NPC", "angry-npc.jpg"),
    ("Макияж клоуна", "clown-makeup.jpg"),
    ("Я что, шутка?", "am-i-joke.jpg"),
]


async def seed_templates():
    """Seed database with meme templates."""
    print("🚀 Seeding templates...")
    
    await init_db()
    
    existing = await get_all_templates()
    existing_filenames = {t["filename"] for t in existing}
    
    added = 0
    skipped = 0
    missing = 0
    
    for name, filename in SEED_TEMPLATES:
        file_path = TEMPLATES_DIR / filename
        
        if not file_path.exists():
            print(f"❌ Missing: {filename}")
            missing += 1
            continue
        
        if filename in existing_filenames:
            print(f"⏭ Exists: {name}")
            skipped += 1
            continue
        
        await add_template(name, filename)
        print(f"✅ Added: {name}")
        added += 1
    
    print(f"\n🎉 Done!")
    print(f"   ✅ Added: {added}")
    print(f"   ⏭ Skipped: {skipped}")
    print(f"   ❌ Missing: {missing}")


async def reset_templates():
    """Reset all templates and re-seed."""
    import aiosqlite
    from config import DB_PATH
    
    print("🔄 Resetting templates...")
    
    await init_db()
    
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("DELETE FROM templates")
        await db.commit()
    
    print("🗑 Old templates removed.\n")
    await seed_templates()


async def list_templates():
    """List all templates in DB."""
    await init_db()
    templates = await get_all_templates()
    
    print(f"📋 Templates in database: {len(templates)}\n")
    for t in templates:
        status = "✅" if t.get("is_active", 1) else "❌"
        print(f"  {status} [{t['id']}] {t['name']} ({t['filename']})")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        cmd = sys.argv[1]
        if cmd == "--reset":
            asyncio.run(reset_templates())
        elif cmd == "--list":
            asyncio.run(list_templates())
        else:
            print("Usage: python seed_templates.py [--reset|--list]")
    else:
        asyncio.run(seed_templates())
