from pyrogram import Client, filters
import psutil
import os

@Client.on_message(filters.command("stopbot") & filters.private)
async def stopbot_handler(client, message):
    user_id = message.from_user.id
    user = users_col.find_one({"USER_ID": user_id}) or {}
    pid = user.get("BOT_PID")

    if not pid:
        await message.reply_text("❌ No running bot found.")
        return

    try:
        proc = psutil.Process(pid)
        proc.terminate()  # You can also use proc.kill() if needed
        await message.reply_text(f"🛑 Sent termination signal to bot process (PID: {pid}).")

        users_col.update_one({"USER_ID": user_id}, {"$set": {"BOT_STATUS": "stopped", "BOT_PID": None}})

    except Exception as e:
        await message.reply_text(f"❌ Failed to stop bot: {str(e)}")