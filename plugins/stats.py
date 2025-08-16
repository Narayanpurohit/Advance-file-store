import logging
from datetime import datetime
from pyrogram import Client, filters
from config import ADMINS
from database import users_col, files_col, stats_col

log = logging.getLogger(__name__)


def count_premium_users(users):
    """Count how many users still have valid premium."""
    now = datetime.utcnow()
    premium_users = 0
    for user in users:
        premium_until = user.get("premium_until")
        if isinstance(premium_until, datetime):
            if premium_until > now:
                premium_users += 1
        elif isinstance(premium_until, str):  # handle string stored time
            try:
                exp = datetime.fromisoformat(premium_until)
                if exp > now:
                    premium_users += 1
            except:
                pass
    return premium_users


@Client.on_message(filters.command("stats") & filters.user(ADMINS))
async def show_stats(client, message):
    try:
        total_users = users_col.count_documents({})
        users = list(users_col.find({}))
        premium_users = count_premium_users(users)

        total_files = files_col.count_documents({})
        stats = stats_col.find_one({"_id": "bot_stats"}) or {}
        total_sent = stats.get("total_files_sent", 0)

        text = (
            "📊 **Bot Statistics** 📊\n\n"
            f"👤 Total Users: `{total_users}`\n"
            f"⭐ Premium Users: `{premium_users}`\n"
            f"📁 Total Files Stored: `{total_files}`\n"
            f"📤 Total Files Sent: `{total_sent}`"
        )

        await message.reply_text(text)
    except Exception as e:
        log.error(f"Error fetching stats: {e}")
        await message.reply_text("❌ Error fetching stats.")