from pyrogram import Client, filters
from config import ADMINS
from database import users_col
import asyncio

@Client.on_message(filters.user(ADMINS) & filters.command("broadcast"))
async def broadcast_command(client, message):
    if len(message.command) < 2:
        return await message.reply_text("Usage: /broadcast Your message here")
    
    text = message.text.split(" ", 1)[1]
    users = users_col.find()
    sent, failed = 0, 0
    await message.reply_text("📢 Broadcast started...")
    for user in users:
        try:
            await client.send_message(user["_id"], text)
            sent += 1
        except:
            failed += 1
        await asyncio.sleep(0.05)
    await message.reply_text(f"✅ Broadcast done.\nSent: {sent}\nFailed: {failed}")