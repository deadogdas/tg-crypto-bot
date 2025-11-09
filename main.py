import asyncio
import os
import sqlite3
from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from aiogram.types import Message
import httpx
from dotenv import load_dotenv

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

DB_PATH = "data/users.db"
os.makedirs("data", exist_ok=True)

def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS allowed_users (
                user_id INTEGER PRIMARY KEY,
                added_by INTEGER
            )
        """)

def is_user_allowed(user_id: int) -> bool:
    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.execute("SELECT 1 FROM allowed_users WHERE user_id = ?", (user_id,))
        return cur.fetchone() is not None

def add_user_by_admin(admin_id: int, target_id: int):
    if not is_user_allowed(admin_id):
        return False, "❌ Только пользователи с доступом могут добавлять."
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            "INSERT OR IGNORE INTO allowed_users (user_id, added_by) VALUES (?, ?)",
            (target_id, admin_id)
        )
    return True, "✅ Пользователь добавлен!"

@dp.message(Command("start"))
async def start(message: Message):
    if is_user_allowed(message.from_user.id):
        await message.answer(
            "✅ Привет! Напиши:\n"
            "• `btc` — Bitcoin\n"
            "• `eth` — Ethereum\n"
            "• `sol` — Solana\n"
            "• `xrp` — Ripple\n"
            "• `doge` — Dogecoin\n"
            "• `ada` — Cardano"
        )
    else:
        await message.answer("❌ У вас нет доступа.")

@dp.message(Command("add_user"))
async def add_user(message: Message):
    if not is_user_allowed(message.from_user.id):
        await message.answer("❌ Только разрешённые пользователи могут добавлять.")
        return
    args = message.text.split()
    if len(args) != 2 or not args[1].isdigit():
        await message.answer("📌 Используйте: /add_user <user_id>")
        return
    user_id = int(args[1])
    success, msg = add_user_by_admin(message.from_user.id, user_id)
    await message.answer(msg)

async def get_crypto_price(symbol: str):
    url = f"https://api.coingecko.com/api/v3/simple/price?ids={symbol}&vs_currencies=usd&include_24hr_change=true"
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.get(url)
            if resp.status_code != 200:
                return None
            data = resp.json()
            if symbol in data and "usd" in data[symbol]:
                return {
                    "symbol": symbol.upper(),
                    "price": data[symbol]["usd"],
                    "change_24h": round(data[symbol].get("usd_24h_change", 0), 2)
                }
    except Exception as e:
        print(f"Ошибка цены для {symbol}: {e}")
    return None

@dp.message()
async def handle_text(message: Message):
    if not is_user_allowed(message.from_user.id):
        await message.answer("❌ У вас нет доступа.")
        return

    text = message.text.strip().lower()

    symbol_map = {
        "btc": "bitcoin",
        "eth": "ethereum",
        "sol": "solana",
        "xrp": "ripple",
        "doge": "dogecoin",
        "ada": "cardano"
    }

    if text in symbol_map:
        coin_id = symbol_map[text]
        price_data = await get_crypto_price(coin_id)
        if price_data:
            ch = price_data["change_24h"]
            emoji = "📈" if ch >= 0 else "📉"
            await message.answer(
                f"💰 {price_data['symbol']}\n"
                f"Цена: ${price_data['price']:,.2f}\n"
                f"24ч: {emoji} {ch:+.2f}%"
            )
        else:
            await message.answer("❌ Не удалось получить данные. Попробуйте позже.")
    else:
        await message.answer(
            "❓ Поддерживаются:\n"
            "`btc`, `eth`, `sol`, `xrp`, `doge`, `ada`"
        )

async def main():
    init_db()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())