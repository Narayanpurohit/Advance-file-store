import datetime
from pyrogram import Client, filters
from database import users_col, stats_col,files_col


def get_total_users():
    return users_col.count_documents({})


def get_premium_users():
    now = datetime.datetime.utcnow()
    return users_col.count_documents({"premium_until": {"$gt": now}})


def get_total_files_sent():
    doc = stats_col.find_one({"_id": "stats"})
    if not doc:
        return 0
    return doc.get("files_sent", 0)


@Client.on_message(filters.command("stats") & filters.private)
async def stats_handler(client, message):
    total_users = get_total_users()
    premium_users = get_premium_users()
    total_files_stored = files_col.count_documents({})
    total_files_sent = get_total_files_sent()
    

    text = (
        f"📊 **Bot Stats** 📊\n\n"
        f"👥 Total Users: `{total_users}`\n"
        f"⭐ Premium Users: `{premium_users}`\n"
         f"📁 Total Files Stored: `{total_files_stored}`\n"
        f"📂 Files Sent: `{total_files_sent}`"
    )

    await message.reply_text(text)