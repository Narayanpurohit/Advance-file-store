from pyrogram import Client, filters
import time
from config import ADMINS
from database import add_premium, remove_premium, is_premium

@Client.on_message(filters.command("add_premium") & filters.user(ADMINS))
async def add_premium_cmd(client, message):
    try:
        # Usage: /add_premium user_id days
        parts = message.text.split()
        if len(parts) != 3:
            await message.reply_text("⚠️ Usage: `/add_premium user_id days`", parse_mode="markdown")
            return

        user_id = int(parts[1])
        days = int(parts[2])

        expiry_time = add_premium(user_id, days)
        await message.reply_text(
            f"✅ Premium given to `{user_id}` for {days} day(s).\n"
            f"📅 Expires: <b>{time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(expiry_time))}</b>",
            parse_mode="html"
        )
    except Exception as e:
        await message.reply_text(f"❌ Error: `{str(e)}`")

@Client.on_message(filters.command("remove_premium") & filters.user(ADMINS))
async def remove_premium_cmd(client, message):
    try:
        # Usage: /remove_premium user_id
        parts = message.text.split()
        if len(parts) != 2:
            await message.reply_text("⚠️ Usage: `/remove_premium user_id`", parse_mode="markdown")
            return

        user_id = int(parts[1])
        remove_premium(user_id)
        await message.reply_text(f"🚫 Premium removed from `{user_id}`")
    except Exception as e:
        await message.reply_text(f"❌ Error: `{str(e)}`")