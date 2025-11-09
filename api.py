from fastapi import FastAPI
import aiohttp

app = FastAPI()

@app.get("/price/{symbol}")
async def get_price(symbol: str):
    symbol = symbol.lower()
    url = f"https://api.coingecko.com/api/v3/simple/price?ids={symbol}&vs_currencies=usd&include_24hr_change=true"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            if resp.status == 200:
                data = await resp.json()
                if symbol in data:
                    return {
                        "symbol": symbol.upper(),
                        "price": data[symbol]["usd"],
                        "change_24h": round(data[symbol].get("usd_24h_change", 0), 2),
                        "currency": "USD"
                    }
            return {"error": "Не удалось получить данные"}

@app.get("/news")
async def get_news():
    return {
        "news": [
            {"title": "Bitcoin растёт!", "source": "CryptoNews", "url": "https://example.com", "date": "2025-11-09"},
            {"title": "Ethereum анонсировал обновление", "source": "The Block", "url": "https://example2.com", "date": "2025-11-08"}
        ]
    }