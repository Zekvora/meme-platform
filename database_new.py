"""
MemePlatform - Enhanced Database
Full system with categories, likes, moderation queue
"""
import aiosqlite
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional
import hashlib
import secrets

from config import DATA_DIR

# Use same database as bot
DATABASE_PATH = DATA_DIR / "memeplatform.db"


async def init_db():
    """Initialize database with all tables."""
    DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)
    
    async with aiosqlite.connect(DATABASE_PATH) as db:
        # Users table
        await db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY,
                telegram_id INTEGER UNIQUE,
                username TEXT,
                email TEXT UNIQUE,
                password_hash TEXT,
                display_name TEXT,
                is_admin INTEGER DEFAULT 0,
                is_banned INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_active TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                uploads_today INTEGER DEFAULT 0,
                uploads_date TEXT
            )
        """)
        
        # Categories table
        await db.execute("""
            CREATE TABLE IF NOT EXISTS categories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                name_en TEXT,
                description TEXT,
                icon TEXT DEFAULT '📁',
                is_active INTEGER DEFAULT 1,
                sort_order INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Memes table (enhanced)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS memes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                author_id INTEGER,
                title TEXT,
                description TEXT,
                filename TEXT NOT NULL,
                file_type TEXT DEFAULT 'image',
                file_size INTEGER DEFAULT 0,
                category_id INTEGER,
                status TEXT DEFAULT 'pending',
                likes_count INTEGER DEFAULT 0,
                views_count INTEGER DEFAULT 0,
                shares_count INTEGER DEFAULT 0,
                is_featured INTEGER DEFAULT 0,
                moderated_by INTEGER,
                moderated_at TIMESTAMP,
                rejection_reason TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (author_id) REFERENCES users(id),
                FOREIGN KEY (category_id) REFERENCES categories(id),
                FOREIGN KEY (moderated_by) REFERENCES users(id)
            )
        """)
        
        # Likes table
        await db.execute("""
            CREATE TABLE IF NOT EXISTS likes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                meme_id INTEGER NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id),
                FOREIGN KEY (meme_id) REFERENCES memes(id),
                UNIQUE(user_id, meme_id)
            )
        """)
        
        # Comments table
        await db.execute("""
            CREATE TABLE IF NOT EXISTS comments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                meme_id INTEGER NOT NULL,
                text TEXT NOT NULL,
                is_hidden INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id),
                FOREIGN KEY (meme_id) REFERENCES memes(id)
            )
        """)
        
        # Direct shares table
        await db.execute("""
            CREATE TABLE IF NOT EXISTS shares (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                meme_id INTEGER NOT NULL,
                sender_id INTEGER NOT NULL,
                recipient_telegram_id INTEGER,
                recipient_email TEXT,
                share_token TEXT UNIQUE,
                is_viewed INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (meme_id) REFERENCES memes(id),
                FOREIGN KEY (sender_id) REFERENCES users(id)
            )
        """)
        
        # Sessions table for web auth
        await db.execute("""
            CREATE TABLE IF NOT EXISTS sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                token TEXT UNIQUE NOT NULL,
                expires_at TIMESTAMP NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        """)
        
        # Activity log
        await db.execute("""
            CREATE TABLE IF NOT EXISTS activity_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                action TEXT NOT NULL,
                details TEXT,
                ip_address TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        """)
        
        # Reports table
        await db.execute("""
            CREATE TABLE IF NOT EXISTS reports (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                meme_id INTEGER NOT NULL,
                reporter_id INTEGER NOT NULL,
                reason TEXT NOT NULL,
                status TEXT DEFAULT 'pending',
                resolved_by INTEGER,
                resolved_at TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (meme_id) REFERENCES memes(id),
                FOREIGN KEY (reporter_id) REFERENCES users(id),
                FOREIGN KEY (resolved_by) REFERENCES users(id)
            )
        """)
        
        # Admin login codes table
        await db.execute("""
            CREATE TABLE IF NOT EXISTS admin_codes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                telegram_id INTEGER NOT NULL,
                code TEXT NOT NULL UNIQUE,
                expires_at TIMESTAMP NOT NULL,
                used INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Default categories
        await db.execute("""
            INSERT OR IGNORE INTO categories (name, name_en, icon, sort_order) VALUES
            ('Животные', 'Animals', '🐱', 1),
            ('Политика', 'Politics', '🏛️', 2),
            ('Приколы', 'Funny', '😂', 3),
            ('Игры', 'Games', '🎮', 4),
            ('Кино и ТВ', 'Movies & TV', '🎬', 5),
            ('IT и программирование', 'IT & Programming', '💻', 6),
            ('Жизненное', 'Life', '🌍', 7),
            ('Другое', 'Other', '📦', 8)
        """)
        
        await db.commit()


# ═══════════════════════════════════════════════
# USER FUNCTIONS
# ═══════════════════════════════════════════════

async def get_or_create_user(telegram_id: int, username: str = None) -> dict:
    """Get or create user by telegram_id."""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        db.row_factory = aiosqlite.Row
        
        cursor = await db.execute(
            "SELECT * FROM users WHERE telegram_id = ?",
            (telegram_id,)
        )
        user = await cursor.fetchone()
        
        if user:
            await db.execute(
                "UPDATE users SET last_active = CURRENT_TIMESTAMP, username = ? WHERE telegram_id = ?",
                (username, telegram_id)
            )
            await db.commit()
            return dict(user)
        
        await db.execute(
            "INSERT INTO users (telegram_id, username, display_name) VALUES (?, ?, ?)",
            (telegram_id, username, username or f"User{telegram_id}")
        )
        await db.commit()
        
        cursor = await db.execute(
            "SELECT * FROM users WHERE telegram_id = ?",
            (telegram_id,)
        )
        return dict(await cursor.fetchone())


async def get_user_by_id(user_id: int) -> Optional[dict]:
    """Get user by ID."""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute("SELECT * FROM users WHERE id = ?", (user_id,))
        row = await cursor.fetchone()
        return dict(row) if row else None


async def get_user_by_email(email: str) -> Optional[dict]:
    """Get user by email."""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute("SELECT * FROM users WHERE email = ?", (email,))
        row = await cursor.fetchone()
        return dict(row) if row else None


async def create_web_user(email: str, password: str, display_name: str) -> dict:
    """Create user for web registration."""
    password_hash = hashlib.sha256(password.encode()).hexdigest()
    
    async with aiosqlite.connect(DATABASE_PATH) as db:
        db.row_factory = aiosqlite.Row
        await db.execute(
            "INSERT INTO users (email, password_hash, display_name) VALUES (?, ?, ?)",
            (email, password_hash, display_name)
        )
        await db.commit()
        
        cursor = await db.execute("SELECT * FROM users WHERE email = ?", (email,))
        return dict(await cursor.fetchone())


async def verify_password(email: str, password: str) -> Optional[dict]:
    """Verify user password."""
    password_hash = hashlib.sha256(password.encode()).hexdigest()
    
    async with aiosqlite.connect(DATABASE_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(
            "SELECT * FROM users WHERE email = ? AND password_hash = ?",
            (email, password_hash)
        )
        row = await cursor.fetchone()
        return dict(row) if row else None


# ═══════════════════════════════════════════════
# SESSION FUNCTIONS
# ═══════════════════════════════════════════════

async def create_session(user_id: int, hours: int = 24 * 7) -> str:
    """Create auth session."""
    token = secrets.token_urlsafe(32)
    expires_at = datetime.now() + timedelta(hours=hours)
    
    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.execute(
            "INSERT INTO sessions (user_id, token, expires_at) VALUES (?, ?, ?)",
            (user_id, token, expires_at.isoformat())
        )
        await db.commit()
    
    return token


async def get_session(token: str) -> Optional[dict]:
    """Get session by token."""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(
            """SELECT s.*, u.* FROM sessions s
               JOIN users u ON s.user_id = u.id
               WHERE s.token = ? AND s.expires_at > CURRENT_TIMESTAMP""",
            (token,)
        )
        row = await cursor.fetchone()
        return dict(row) if row else None


async def delete_session(token: str):
    """Delete session."""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.execute("DELETE FROM sessions WHERE token = ?", (token,))
        await db.commit()


# ═══════════════════════════════════════════════
# ADMIN LOGIN CODES
# ═══════════════════════════════════════════════

async def generate_admin_code(telegram_id: int, minutes: int = 5) -> str:
    """Generate one-time admin login code."""
    code = secrets.token_urlsafe(16)
    expires_at = datetime.now() + timedelta(minutes=minutes)
    
    async with aiosqlite.connect(DATABASE_PATH) as db:
        # Delete old codes for this user
        await db.execute(
            "DELETE FROM admin_codes WHERE telegram_id = ?",
            (telegram_id,)
        )
        # Create new code
        await db.execute(
            "INSERT INTO admin_codes (telegram_id, code, expires_at) VALUES (?, ?, ?)",
            (telegram_id, code, expires_at.isoformat())
        )
        await db.commit()
    
    return code


async def verify_admin_code(telegram_id: int, code: str) -> bool:
    """Verify admin login code."""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        cursor = await db.execute(
            """SELECT * FROM admin_codes 
               WHERE telegram_id = ? AND code = ? AND used = 0 
               AND expires_at > CURRENT_TIMESTAMP""",
            (telegram_id, code)
        )
        row = await cursor.fetchone()
        
        if row:
            # Mark code as used
            await db.execute(
                "UPDATE admin_codes SET used = 1 WHERE telegram_id = ? AND code = ?",
                (telegram_id, code)
            )
            await db.commit()
            return True
        
        return False


async def get_user_by_telegram_id(telegram_id: int) -> Optional[dict]:
    """Get user by telegram ID."""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(
            "SELECT * FROM users WHERE telegram_id = ?",
            (telegram_id,)
        )
        row = await cursor.fetchone()
        return dict(row) if row else None


async def ensure_admin_user(telegram_id: int, username: str = None) -> dict:
    """Ensure admin user exists in database."""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        db.row_factory = aiosqlite.Row
        
        cursor = await db.execute(
            "SELECT * FROM users WHERE telegram_id = ?",
            (telegram_id,)
        )
        user = await cursor.fetchone()
        
        if user:
            # Update admin status
            await db.execute(
                "UPDATE users SET is_admin = 1, last_active = CURRENT_TIMESTAMP WHERE telegram_id = ?",
                (telegram_id,)
            )
            await db.commit()
            cursor = await db.execute(
                "SELECT * FROM users WHERE telegram_id = ?",
                (telegram_id,)
            )
            return dict(await cursor.fetchone())
        
        # Create new admin user
        await db.execute(
            "INSERT INTO users (telegram_id, username, display_name, is_admin) VALUES (?, ?, ?, 1)",
            (telegram_id, username, username or f"Admin{telegram_id}")
        )
        await db.commit()
        
        cursor = await db.execute(
            "SELECT * FROM users WHERE telegram_id = ?",
            (telegram_id,)
        )
        return dict(await cursor.fetchone())


# ═══════════════════════════════════════════════
# CATEGORY FUNCTIONS
# ═══════════════════════════════════════════════

async def get_categories() -> list:
    """Get all active categories."""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(
            "SELECT * FROM categories WHERE is_active = 1 ORDER BY sort_order"
        )
        return [dict(row) for row in await cursor.fetchall()]


async def get_category_by_id(category_id: int) -> Optional[dict]:
    """Get category by ID."""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute("SELECT * FROM categories WHERE id = ?", (category_id,))
        row = await cursor.fetchone()
        return dict(row) if row else None


async def create_category(name: str, name_en: str = None, icon: str = "📁", description: str = None) -> int:
    """Create new category."""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        cursor = await db.execute(
            "INSERT INTO categories (name, name_en, icon, description) VALUES (?, ?, ?, ?)",
            (name, name_en, icon, description)
        )
        await db.commit()
        return cursor.lastrowid


async def update_category(category_id: int, **kwargs):
    """Update category fields."""
    if not kwargs:
        return
    async with aiosqlite.connect(DATABASE_PATH) as db:
        fields = ", ".join(f"{k} = ?" for k in kwargs.keys())
        values = list(kwargs.values()) + [category_id]
        await db.execute(f"UPDATE categories SET {fields} WHERE id = ?", values)
        await db.commit()


async def delete_category(category_id: int):
    """Delete category."""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.execute("UPDATE memes SET category_id = NULL WHERE category_id = ?", (category_id,))
        await db.execute("DELETE FROM categories WHERE id = ?", (category_id,))
        await db.commit()


# ═══════════════════════════════════════════════
# MEME FUNCTIONS
# ═══════════════════════════════════════════════

async def create_meme(
    author_id: int,
    filename: str,
    title: str = None,
    description: str = None,
    category_id: int = None,
    file_type: str = "image",
    file_size: int = 0
) -> int:
    """Create new meme (pending status)."""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        cursor = await db.execute(
            """INSERT INTO memes 
               (author_id, filename, title, description, category_id, file_type, file_size)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (author_id, filename, title, description, category_id, file_type, file_size)
        )
        await db.commit()
        return cursor.lastrowid


async def get_meme_by_id(meme_id: int) -> Optional[dict]:
    """Get meme by ID with author and category info."""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(
            """SELECT m.*, u.username as author_name, u.display_name as author_display,
                      c.name as category_name, c.icon as category_icon
               FROM memes m
               LEFT JOIN users u ON m.author_id = u.id
               LEFT JOIN categories c ON m.category_id = c.id
               WHERE m.id = ?""",
            (meme_id,)
        )
        row = await cursor.fetchone()
        return dict(row) if row else None


async def get_memes(
    status: str = "approved",
    category_id: int = None,
    author_id: int = None,
    search: str = None,
    sort_by: str = "created_at",
    sort_order: str = "DESC",
    limit: int = 50,
    offset: int = 0
) -> list:
    """Get memes with filters."""
    query = """
        SELECT m.*, u.username as author_name, u.display_name as author_display,
               c.name as category_name, c.icon as category_icon
        FROM memes m
        LEFT JOIN users u ON m.author_id = u.id
        LEFT JOIN categories c ON m.category_id = c.id
        WHERE 1=1
    """
    params = []
    
    if status:
        query += " AND m.status = ?"
        params.append(status)
    
    if category_id:
        query += " AND m.category_id = ?"
        params.append(category_id)
    
    if author_id:
        query += " AND m.author_id = ?"
        params.append(author_id)
    
    if search:
        query += " AND (m.title LIKE ? OR m.description LIKE ?)"
        params.extend([f"%{search}%", f"%{search}%"])
    
    # Validate sort_by to prevent SQL injection
    valid_sorts = ["created_at", "likes_count", "views_count", "title"]
    if sort_by not in valid_sorts:
        sort_by = "created_at"
    
    sort_order = "DESC" if sort_order.upper() == "DESC" else "ASC"
    query += f" ORDER BY m.{sort_by} {sort_order} LIMIT ? OFFSET ?"
    params.extend([limit, offset])
    
    async with aiosqlite.connect(DATABASE_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(query, params)
        return [dict(row) for row in await cursor.fetchall()]


async def count_memes(
    status: str = "approved",
    category_id: int = None,
    author_id: int = None,
    search: str = None
) -> int:
    """Count memes with filters."""
    query = "SELECT COUNT(*) FROM memes m WHERE 1=1"
    params = []
    
    if status:
        query += " AND m.status = ?"
        params.append(status)
    
    if category_id:
        query += " AND m.category_id = ?"
        params.append(category_id)
    
    if author_id:
        query += " AND m.author_id = ?"
        params.append(author_id)
    
    if search:
        query += " AND (m.title LIKE ? OR m.description LIKE ?)"
        params.extend([f"%{search}%", f"%{search}%"])
    
    async with aiosqlite.connect(DATABASE_PATH) as db:
        cursor = await db.execute(query, params)
        row = await cursor.fetchone()
        return row[0] if row else 0


async def get_pending_memes(limit: int = 50) -> list:
    """Get pending memes for moderation."""
    return await get_memes(status="pending", limit=limit, sort_by="created_at", sort_order="ASC")


async def get_user_memes(user_id: int, status: str = None) -> list:
    """Get memes by user."""
    return await get_memes(status=status, author_id=user_id)


async def approve_meme(meme_id: int, moderator_id: int):
    """Approve meme."""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.execute(
            """UPDATE memes SET status = 'approved', moderated_by = ?, 
               moderated_at = CURRENT_TIMESTAMP WHERE id = ?""",
            (moderator_id, meme_id)
        )
        await db.commit()


async def reject_meme(meme_id: int, moderator_id: int, reason: str = None):
    """Reject meme."""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.execute(
            """UPDATE memes SET status = 'rejected', moderated_by = ?, 
               moderated_at = CURRENT_TIMESTAMP, rejection_reason = ? WHERE id = ?""",
            (moderator_id, reason, meme_id)
        )
        await db.commit()


async def delete_meme(meme_id: int):
    """Delete meme."""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.execute("DELETE FROM likes WHERE meme_id = ?", (meme_id,))
        await db.execute("DELETE FROM comments WHERE meme_id = ?", (meme_id,))
        await db.execute("DELETE FROM shares WHERE meme_id = ?", (meme_id,))
        await db.execute("DELETE FROM memes WHERE id = ?", (meme_id,))
        await db.commit()


async def update_meme(meme_id: int, **kwargs):
    """Update meme fields."""
    allowed = ["title", "description", "category_id", "is_featured", "status"]
    updates = {k: v for k, v in kwargs.items() if k in allowed}
    
    if not updates:
        return
    
    set_clause = ", ".join(f"{k} = ?" for k in updates.keys())
    values = list(updates.values()) + [meme_id]
    
    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.execute(
            f"UPDATE memes SET {set_clause}, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
            values
        )
        await db.commit()


async def increment_views(meme_id: int):
    """Increment view count."""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.execute(
            "UPDATE memes SET views_count = views_count + 1 WHERE id = ?",
            (meme_id,)
        )
        await db.commit()


# ═══════════════════════════════════════════════
# LIKE FUNCTIONS
# ═══════════════════════════════════════════════

async def toggle_like(user_id: int, meme_id: int) -> bool:
    """Toggle like on meme. Returns True if liked, False if unliked."""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        cursor = await db.execute(
            "SELECT id FROM likes WHERE user_id = ? AND meme_id = ?",
            (user_id, meme_id)
        )
        existing = await cursor.fetchone()
        
        if existing:
            await db.execute(
                "DELETE FROM likes WHERE user_id = ? AND meme_id = ?",
                (user_id, meme_id)
            )
            await db.execute(
                "UPDATE memes SET likes_count = likes_count - 1 WHERE id = ?",
                (meme_id,)
            )
            await db.commit()
            return False
        else:
            await db.execute(
                "INSERT INTO likes (user_id, meme_id) VALUES (?, ?)",
                (user_id, meme_id)
            )
            await db.execute(
                "UPDATE memes SET likes_count = likes_count + 1 WHERE id = ?",
                (meme_id,)
            )
            await db.commit()
            return True


async def has_liked(user_id: int, meme_id: int) -> bool:
    """Check if user liked meme."""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        cursor = await db.execute(
            "SELECT id FROM likes WHERE user_id = ? AND meme_id = ?",
            (user_id, meme_id)
        )
        return await cursor.fetchone() is not None


# ═══════════════════════════════════════════════
# SHARE FUNCTIONS
# ═══════════════════════════════════════════════

async def create_share(meme_id: int, sender_id: int, recipient_telegram_id: int = None) -> str:
    """Create share link."""
    token = secrets.token_urlsafe(16)
    
    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.execute(
            """INSERT INTO shares (meme_id, sender_id, recipient_telegram_id, share_token)
               VALUES (?, ?, ?, ?)""",
            (meme_id, sender_id, recipient_telegram_id, token)
        )
        await db.execute(
            "UPDATE memes SET shares_count = shares_count + 1 WHERE id = ?",
            (meme_id,)
        )
        await db.commit()
    
    return token


async def get_share_by_token(token: str) -> Optional[dict]:
    """Get share by token."""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(
            """SELECT s.*, m.*, u.display_name as sender_name
               FROM shares s
               JOIN memes m ON s.meme_id = m.id
               JOIN users u ON s.sender_id = u.id
               WHERE s.share_token = ?""",
            (token,)
        )
        row = await cursor.fetchone()
        if row:
            await db.execute(
                "UPDATE shares SET is_viewed = 1 WHERE share_token = ?",
                (token,)
            )
            await db.commit()
        return dict(row) if row else None


# ═══════════════════════════════════════════════
# STATISTICS
# ═══════════════════════════════════════════════

async def get_stats() -> dict:
    """Get platform statistics."""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        stats = {}
        
        cursor = await db.execute("SELECT COUNT(*) FROM users")
        stats["total_users"] = (await cursor.fetchone())[0]
        
        cursor = await db.execute("SELECT COUNT(*) FROM memes")
        stats["total_memes"] = (await cursor.fetchone())[0]
        
        cursor = await db.execute("SELECT COUNT(*) FROM memes WHERE status = 'approved'")
        stats["approved_memes"] = (await cursor.fetchone())[0]
        
        cursor = await db.execute("SELECT COUNT(*) FROM memes WHERE status = 'pending'")
        stats["pending_memes"] = (await cursor.fetchone())[0]
        
        cursor = await db.execute("SELECT COUNT(*) FROM memes WHERE status = 'rejected'")
        stats["rejected_memes"] = (await cursor.fetchone())[0]
        
        cursor = await db.execute("SELECT SUM(likes_count) FROM memes")
        stats["total_likes"] = (await cursor.fetchone())[0] or 0
        
        cursor = await db.execute("SELECT SUM(views_count) FROM memes")
        stats["total_views"] = (await cursor.fetchone())[0] or 0
        
        cursor = await db.execute("SELECT SUM(shares_count) FROM memes")
        stats["total_shares"] = (await cursor.fetchone())[0] or 0
        
        cursor = await db.execute("SELECT COUNT(*) FROM reports WHERE status = 'open'")
        stats["open_reports"] = (await cursor.fetchone())[0]
        
        # Today's activity
        today = datetime.now().date().isoformat()
        cursor = await db.execute(
            "SELECT COUNT(*) FROM memes WHERE DATE(created_at) = ?",
            (today,)
        )
        stats["today_uploads"] = (await cursor.fetchone())[0]
        
        cursor = await db.execute(
            "SELECT COUNT(*) FROM users WHERE DATE(created_at) = ?",
            (today,)
        )
        stats["users_today"] = (await cursor.fetchone())[0]
        
        return stats


async def get_top_memes(limit: int = 10) -> list:
    """Get top memes by likes."""
    return await get_memes(status="approved", sort_by="likes_count", limit=limit)


async def get_category_stats() -> list:
    """Get meme count per category."""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(
            """SELECT c.*, COUNT(m.id) as meme_count
               FROM categories c
               LEFT JOIN memes m ON c.id = m.category_id AND m.status = 'approved'
               WHERE c.is_active = 1
               GROUP BY c.id
               ORDER BY meme_count DESC"""
        )
        return [dict(row) for row in await cursor.fetchall()]


# ═══════════════════════════════════════════════
# BULK OPERATIONS
# ═══════════════════════════════════════════════

async def bulk_approve(meme_ids: list, moderator_id: int):
    """Bulk approve memes."""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        for meme_id in meme_ids:
            await db.execute(
                """UPDATE memes SET status = 'approved', moderated_by = ?,
                   moderated_at = CURRENT_TIMESTAMP WHERE id = ?""",
                (moderator_id, meme_id)
            )
        await db.commit()


async def bulk_reject(meme_ids: list, moderator_id: int, reason: str = None):
    """Bulk reject memes."""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        for meme_id in meme_ids:
            await db.execute(
                """UPDATE memes SET status = 'rejected', moderated_by = ?,
                   moderated_at = CURRENT_TIMESTAMP, rejection_reason = ? WHERE id = ?""",
                (moderator_id, reason, meme_id)
            )
        await db.commit()


async def bulk_delete(meme_ids: list):
    """Bulk delete memes."""
    for meme_id in meme_ids:
        await delete_meme(meme_id)
