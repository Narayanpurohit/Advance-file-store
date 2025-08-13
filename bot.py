import asyncio
from pyrogram import Client
from config import BOT_TOKEN
import config
import os

# Start Pyrogram client
app = Client(
    "fileshare_bot",
    bot_token=BOT_TOKEN,
    api_id=config.API_ID,
    api_hash=config.API_HASH,
    plugins={"root": "plugins"}
)

async def main():
    async with app:
        me = await app.get_me()
        config.BOT_USERNAME = me.username
        print(f"✅ Bot started as @{config.BOT_USERNAME}")
        await idle()

if __name__ == "__main__":
    from pyrogram import idle
    asyncio.run(main())