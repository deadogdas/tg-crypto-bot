# ЗАМЕНИ НА СВОЙ TELEGRAM ID!
MY_TELEGRAM_ID = 123456789

import sqlite3
import os
os.makedirs("data", exist_ok=True)

with sqlite3.connect("data/users.db") as conn:
    conn.execute("""
        CREATE TABLE IF NOT EXISTS allowed_users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            added_by INTEGER
        )
    """)
    conn.execute(
        "INSERT OR IGNORE INTO allowed_users (user_id, added_by) VALUES (?, ?)",
        (MY_TELEGRAM_ID, MY_TELEGRAM_ID)
    )
print("✅ Ты добавлен как админ!")