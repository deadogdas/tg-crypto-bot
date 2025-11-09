import sqlite3
import os

DB_PATH = "data/users.db"

# Убедимся, что папка data существует
os.makedirs("data", exist_ok=True)

def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS allowed_users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                added_by INTEGER
            )
        """)

def is_user_allowed(user_id: int) -> bool:
    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.execute("SELECT 1 FROM allowed_users WHERE user_id = ?", (user_id,))
        return cur.fetchone() is not None

def add_user_by_admin(admin_id: int, target_id: int, username: str = None):
    if not is_user_allowed(admin_id):
        return False, "Только пользователи с доступом могут добавлять других."
    with sqlite3.connect(DB_PATH) as conn:
        try:
            conn.execute(
                "INSERT OR IGNORE INTO allowed_users (user_id, username, added_by) VALUES (?, ?, ?)",
                (target_id, username, admin_id)
            )
            return True, "✅ Пользователь добавлен!"
        except Exception as e:
            return False, f"❌ Ошибка: {e}"