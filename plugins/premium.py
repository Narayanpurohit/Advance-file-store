from pyrogram import Client, filters
from config import ADMINS
from database import add_premium, remove_premium, is_premium
import datetime

@Client.on_message(filters.user(ADMINS) & filters.command("addpremium"))
async def add_premium_cmd(client, message):
    try:
        user_id = int(message.command[1])
        hours = int(message.command[2])
    except:
        return await message.reply_text("Usage: /addpremium user_id hours")
    add_premium(user_id, hours)
    await message.reply_text(f"✅ Premium given to {user_id} for {hours} hours.")

@Client.on_message(filters.user(ADMINS) & filters.command("removepremium"))
async def remove_premium_cmd(client, message):
    try:
        user_id = int(message.command[1])
    except:
        return await message.reply_text("Usage: /removepremium user_id")
    remove_premium(user_id)
    await message.reply_text(f"❌ Premium removed from {user_id}")

@Client.on_message(filters.command("mypremium"))
async def my_premium_cmd(client, message):
    if is_premium(message.from_user.id):
        expiry = datetime.datetime.utcnow()  # placeholder, you can show real expiry if needed
        await message.reply_text(f"🌟 You are premium!")
    else:
        await message.reply_text("❌ You are not premium.")