"""
Create admin user for MemePlatform
Usage: python create_admin.py email password
"""
import asyncio
import sys
import hashlib
from database_new import DATABASE_PATH, init_db
import aiosqlite


async def create_admin(email: str, password: str, display_name: str = "Admin"):
    """Create admin user."""
    await init_db()
    
    password_hash = hashlib.sha256(password.encode()).hexdigest()
    
    async with aiosqlite.connect(DATABASE_PATH) as db:
        # Check if exists
        cursor = await db.execute("SELECT id FROM users WHERE email = ?", (email,))
        existing = await cursor.fetchone()
        
        if existing:
            # Update to admin
            await db.execute(
                "UPDATE users SET is_admin = 1, password_hash = ? WHERE email = ?",
                (password_hash, email)
            )
            print(f"✅ Пользователь {email} обновлён до администратора")
        else:
            # Create new admin
            await db.execute(
                """INSERT INTO users (email, password_hash, display_name, is_admin) 
                   VALUES (?, ?, ?, 1)""",
                (email, password_hash, display_name)
            )
            print(f"✅ Администратор создан: {email}")
        
        await db.commit()


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Использование: python create_admin.py email password [display_name]")
        print("Пример: python create_admin.py admin@example.com mypassword Admin")
        sys.exit(1)
    
    email = sys.argv[1]
    password = sys.argv[2]
    display_name = sys.argv[3] if len(sys.argv) > 3 else "Admin"
    
    asyncio.run(create_admin(email, password, display_name))
