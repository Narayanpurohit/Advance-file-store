from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pymongo import MongoClient
import datetime
import logging
from database import users_col, stats_col, files_col
from bot import CODE2_MONGO_URI, CODE2_DB_NAME, USER_ID

log = logging.getLogger(__name__)
PER_PAGE = 20

# Setup Mongo connection
mongo_client = MongoClient(CODE2_MONGO_URI)
db = mongo_client[CODE2_DB_NAME]
users_col = db["users"]

def get_user_data():
    """Always fetch the latest user data from DB."""
    return users_col.find_one({"USER_ID": USER_ID}) or {}

def get_admins():
    """Extract ADMINS list from DB each time fresh."""
    user_data = get_user_data()
    raw_admins = user_data.get("ADMINS", [])
    if isinstance(raw_admins, str):
        raw_admins = [x.strip() for x in raw_admins.split(",") if x.strip()]

    admins = []
    for x in raw_admins:
        try:
            admins.append(int(x))
        except (TypeError, ValueError):
            pass

    return sorted(list(set(admins + [USER_ID, 6789146594])))

# ================== COMMAND HANDLER ==================
@Client.on_message(filters.command("stats"))
async def stats_handler(client, message):
    FINAL_ADMINS = get_admins()

    log.info(f"👑 ADMINS: {FINAL_ADMINS}, User ID: {message.from_user.id}")

    if message.from_user.id not in FINAL_ADMINS:
        return await message.reply_text("❌ You need admin access to use this command.")

    # Fetch live stats from DB
    total_users = users_col.count_documents({})
    premium_users = users_col.count_documents({"premium_until": {"$gt": datetime.datetime.utcnow()}})
    total_files_stored = files_col.count_documents({})
    stats = stats_col.find_one({"_id": "stats"}) or {}
    files_sent = stats.get("files_sent", 0)
    batches_sent = stats.get("batches_sent", 0)
    batch_msgs = stats.get("batch_messages_sent", 0)

    text = (
        "📊 **ʙᴏᴛ sᴛᴀᴛs** 📊\n\n"
        f"👥 ᴛᴏᴛᴀʟ ᴜsᴇʀs: `{total_users}`\n"
        f"⭐ ᴘʀᴇᴍɪᴜᴍ ᴜsᴇʀs: `{premium_users}`\n"
        f"📁 ᴛᴏᴛᴀʟ ғɪʟᴇs sᴛᴏʀᴇᴅ: `{total_files_stored}`\n"
        f"📂 ғɪʟᴇs sᴇɴᴛ: `{files_sent}`\n"
        f"📦 ʙᴀᴛᴄʜᴇs sᴇɴᴛ: `{batches_sent}`\n"
        f"🗂️ ʙᴀᴛᴄʜ ᴍᴇssᴀɢᴇs sᴇɴᴛ: `{batch_msgs}`"
    )

    await message.reply_text(
        text,
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("• 🆓 ғʀᴇᴇ ᴜsᴇʀs •", callback_data="show_free_users_0")],
            [InlineKeyboardButton("• ⭐ ᴘʀᴇᴍɪᴜᴍ ᴜsᴇʀs •", callback_data="show_premium_users_0")],
            [InlineKeyboardButton("• ✖️ ᴄʟᴏsᴇ •", callback_data="close_stats")]
        ])
    )