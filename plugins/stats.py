from pyrogram import Client, filters
from database import get_stat
from config import ADMINS

@Client.on_message(filters.user(ADMINS) & filters.command("stats"))
async def stats_command(client, message):
    total_users, files_sent = get_stat()
    await message.reply_text(f"📊 **Bot Stats**\n👥 Users: {total_users}\n📤 Files Sent: {files_sent}")