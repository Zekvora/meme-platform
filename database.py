"""
MemeMakerBot - Database (SQLite + aiosqlite)
"""
import aiosqlite
from datetime import datetime
from config import DB_PATH


async def init_db():
    """Initialize database tables."""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.executescript("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                first_name TEXT,
                language TEXT DEFAULT 'ru',
                created_at TEXT,
                last_active TEXT,
                is_banned INTEGER DEFAULT 0,
                uploads_today INTEGER DEFAULT 0,
                last_upload_date TEXT
            );
            
            CREATE TABLE IF NOT EXISTS templates (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                filename TEXT NOT NULL UNIQUE,
                is_active INTEGER DEFAULT 1,
                usage_count INTEGER DEFAULT 0,
                created_at TEXT,
                uploaded_by INTEGER DEFAULT 0,
                is_user_upload INTEGER DEFAULT 0,
                moderation_status TEXT DEFAULT 'approved'
            );
            
            CREATE TABLE IF NOT EXISTS memes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                template_id INTEGER,
                top_text TEXT,
                bottom_text TEXT,
                created_at TEXT
            );
            
            CREATE TABLE IF NOT EXISTS stats (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                event_type TEXT,
                user_id INTEGER,
                details TEXT,
                created_at TEXT
            );
            
            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT
            );
        """)
        await db.commit()
        
        # Migration: Add new columns if they don't exist
        # Check users table
        cursor = await db.execute("PRAGMA table_info(users)")
        columns = {row[1] for row in await cursor.fetchall()}
        
        if "uploads_today" not in columns:
            await db.execute("ALTER TABLE users ADD COLUMN uploads_today INTEGER DEFAULT 0")
        if "last_upload_date" not in columns:
            await db.execute("ALTER TABLE users ADD COLUMN last_upload_date TEXT")
        
        # Check templates table
        cursor = await db.execute("PRAGMA table_info(templates)")
        columns = {row[1] for row in await cursor.fetchall()}
        
        if "uploaded_by" not in columns:
            await db.execute("ALTER TABLE templates ADD COLUMN uploaded_by INTEGER DEFAULT 0")
        if "is_user_upload" not in columns:
            await db.execute("ALTER TABLE templates ADD COLUMN is_user_upload INTEGER DEFAULT 0")
        if "moderation_status" not in columns:
            await db.execute("ALTER TABLE templates ADD COLUMN moderation_status TEXT DEFAULT 'approved'")
        
        await db.commit()


# === Users ===
async def get_or_create_user(user_id: int, username: str = None, first_name: str = None, language: str = "ru") -> dict:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
        row = await cursor.fetchone()
        
        now = datetime.now().isoformat()
        
        if row:
            await db.execute(
                "UPDATE users SET last_active = ?, username = ?, first_name = ? WHERE user_id = ?",
                (now, username, first_name, user_id)
            )
            await db.commit()
            return dict(row)
        else:
            await db.execute(
                "INSERT INTO users (user_id, username, first_name, language, created_at, last_active) VALUES (?, ?, ?, ?, ?, ?)",
                (user_id, username, first_name, language, now, now)
            )
            await db.commit()
            return {"user_id": user_id, "username": username, "first_name": first_name, "language": language}


async def get_user_language(user_id: int) -> str:
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute("SELECT language FROM users WHERE user_id = ?", (user_id,))
        row = await cursor.fetchone()
        return row[0] if row else "ru"


async def set_user_language(user_id: int, language: str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("UPDATE users SET language = ? WHERE user_id = ?", (language, user_id))
        await db.commit()


async def get_all_user_ids() -> list[int]:
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute("SELECT user_id FROM users WHERE is_banned = 0")
        rows = await cursor.fetchall()
        return [row[0] for row in rows]


async def get_users_count() -> int:
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute("SELECT COUNT(*) FROM users")
        row = await cursor.fetchone()
        return row[0] if row else 0


# === Templates ===
async def get_active_templates() -> list[dict]:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute("SELECT * FROM templates WHERE is_active = 1 ORDER BY usage_count DESC")
        rows = await cursor.fetchall()
        return [dict(row) for row in rows]


async def get_template_by_id(template_id: int) -> dict | None:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute("SELECT * FROM templates WHERE id = ?", (template_id,))
        row = await cursor.fetchone()
        return dict(row) if row else None


async def add_template(name: str, filename: str) -> int:
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            "INSERT INTO templates (name, filename, created_at) VALUES (?, ?, ?)",
            (name, filename, datetime.now().isoformat())
        )
        await db.commit()
        return cursor.lastrowid


async def delete_template(template_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("DELETE FROM templates WHERE id = ?", (template_id,))
        await db.commit()


async def toggle_template(template_id: int, is_active: bool):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("UPDATE templates SET is_active = ? WHERE id = ?", (1 if is_active else 0, template_id))
        await db.commit()


async def increment_template_usage(template_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("UPDATE templates SET usage_count = usage_count + 1 WHERE id = ?", (template_id,))
        await db.commit()


async def get_templates_count() -> int:
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute("SELECT COUNT(*) FROM templates")
        row = await cursor.fetchone()
        return row[0] if row else 0


async def get_all_templates() -> list[dict]:
    """Get all templates including inactive."""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute("SELECT * FROM templates ORDER BY id DESC")
        rows = await cursor.fetchall()
        return [dict(row) for row in rows]


# === Memes ===
async def save_meme(user_id: int, template_id: int, top_text: str = None, bottom_text: str = None):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT INTO memes (user_id, template_id, top_text, bottom_text, created_at) VALUES (?, ?, ?, ?, ?)",
            (user_id, template_id, top_text, bottom_text, datetime.now().isoformat())
        )
        await db.commit()


async def get_memes_count() -> int:
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute("SELECT COUNT(*) FROM memes")
        row = await cursor.fetchone()
        return row[0] if row else 0


# === Stats ===
async def log_event(event_type: str, user_id: int = None, details: str = None):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT INTO stats (event_type, user_id, details, created_at) VALUES (?, ?, ?, ?)",
            (event_type, user_id, details, datetime.now().isoformat())
        )
        await db.commit()


async def get_errors_count() -> int:
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute("SELECT COUNT(*) FROM stats WHERE event_type = 'error'")
        row = await cursor.fetchone()
        return row[0] if row else 0


# === Settings ===
async def get_setting(key: str, default: str = None) -> str | None:
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute("SELECT value FROM settings WHERE key = ?", (key,))
        row = await cursor.fetchone()
        return row[0] if row else default


async def set_setting(key: str, value: str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)",
            (key, value)
        )
        await db.commit()


# === User Uploads ===
async def add_user_template(name: str, filename: str, user_id: int) -> int:
    """Add user-uploaded template (pending moderation)."""
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            """INSERT INTO templates 
               (name, filename, created_at, uploaded_by, is_user_upload, moderation_status, is_active) 
               VALUES (?, ?, ?, ?, 1, 'pending', 0)""",
            (name, filename, datetime.now().isoformat(), user_id)
        )
        await db.commit()
        return cursor.lastrowid


async def get_pending_templates() -> list[dict]:
    """Get templates pending moderation."""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(
            "SELECT * FROM templates WHERE moderation_status = 'pending' ORDER BY id DESC"
        )
        rows = await cursor.fetchall()
        return [dict(row) for row in rows]


async def approve_template(template_id: int):
    """Approve user-uploaded template."""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "UPDATE templates SET moderation_status = 'approved', is_active = 1 WHERE id = ?",
            (template_id,)
        )
        await db.commit()


async def reject_template(template_id: int):
    """Reject and delete user-uploaded template."""
    async with aiosqlite.connect(DB_PATH) as db:
        # Get filename to delete file
        cursor = await db.execute("SELECT filename FROM templates WHERE id = ?", (template_id,))
        row = await cursor.fetchone()
        if row:
            from config import TEMPLATES_DIR
            file_path = TEMPLATES_DIR / row[0]
            if file_path.exists():
                file_path.unlink()
        
        await db.execute("DELETE FROM templates WHERE id = ?", (template_id,))
        await db.commit()


async def get_user_uploads_today(user_id: int) -> int:
    """Get user's upload count for today."""
    async with aiosqlite.connect(DB_PATH) as db:
        today = datetime.now().strftime("%Y-%m-%d")
        cursor = await db.execute(
            "SELECT uploads_today, last_upload_date FROM users WHERE user_id = ?",
            (user_id,)
        )
        row = await cursor.fetchone()
        
        if not row:
            return 0
        
        uploads_today, last_upload_date = row
        
        # Reset counter if it's a new day
        if last_upload_date != today:
            await db.execute(
                "UPDATE users SET uploads_today = 0, last_upload_date = ? WHERE user_id = ?",
                (today, user_id)
            )
            await db.commit()
            return 0
        
        return uploads_today or 0


async def increment_user_uploads(user_id: int):
    """Increment user's upload counter."""
    async with aiosqlite.connect(DB_PATH) as db:
        today = datetime.now().strftime("%Y-%m-%d")
        await db.execute(
            """UPDATE users SET 
               uploads_today = COALESCE(uploads_today, 0) + 1,
               last_upload_date = ?
               WHERE user_id = ?""",
            (today, user_id)
        )
        await db.commit()


async def get_pending_count() -> int:
    """Get count of pending templates."""
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            "SELECT COUNT(*) FROM templates WHERE moderation_status = 'pending'"
        )
        row = await cursor.fetchone()
        return row[0] if row else 0
