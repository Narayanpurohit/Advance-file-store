# plugins/stats.py

import datetime
from pyrogram import Client, filters
from config import ADMINS
from database import get_all_users, get_total_files_sent

@Client.on_message(filters.command("stats") & filters.user(ADMINS))
async def stats_handler(client, message):
    users = get_all_users()
    total_users = len(users)

    now = datetime.datetime.utcnow()
    premium_users = 0

    for user in users:
        if user.get("premium_until") and user["premium_until"] > now:
            premium_users += 1

    total_files_sent = get_total_files_sent()

    await message.reply_text(
        f"📊 **Bot Stats**\n\n"
        f"👥 Total Users: `{total_users}`\n"
        f"💎 Premium Users: `{premium_users}`\n"
        f"📤 Total Files Sent: `{total_files_sent}`"
    )