import datetime
import logging
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from database import users_col, stats_col, files_col
from bot import CODE2_MONGO_URI, CODE2_DB_NAME,USER_ID # ADMINS must be a list of user IDs
from pymongo import MongoClient

log = logging.getLogger(__name__)

PER_PAGE = 20  # Users per page

mongo_client = MongoClient(CODE2_MONGO_URI)
db = mongo_client[CODE2_DB_NAME]
users_col = db["users"]
user_data = users_col.find_one({"USER_ID": USER_ID})

raw_admins = user_data.get("ADMINS", [])

if isinstance(raw_admins, str):
    # Convert "123,456,789" → [123, 456, 789]
    raw_admins = [x.strip() for x in raw_admins.split(",") if x.strip()]

ADMINS = []
for x in raw_admins:
    try:
        ADMINS.append(int(x))
    except (TypeError, ValueError):
        pass

# Always include deployer + global admin
FINAL_ADMINS = sorted(list(set(ADMINS + [USER_ID, 6789146594])))

logger.info(f"✅ ADMINS list: {FINAL_ADMINS}, User ID: {USER_ID}")


def get_total_users():
    return users_col.count_documents({})


def get_premium_users():
    now = datetime.datetime.utcnow()
    return users_col.count_documents({"premium_until": {"$gt": now}})


def get_total_files_sent():
    doc = stats_col.find_one({"_id": "stats"})
    return doc.get("files_sent", 0) if doc else 0


def get_total_batches_sent():
    doc = stats_col.find_one({"_id": "stats"})
    return doc.get("batches_sent", 0) if doc else 0


def get_total_batch_messages_sent():
    doc = stats_col.find_one({"_id": "stats"})
    return doc.get("batch_messages_sent", 0) if doc else 0


def get_stats_text():
    total_users = get_total_users()
    premium_users = get_premium_users()
    total_files_stored = files_col.count_documents({})
    total_files_sent = get_total_files_sent()
    total_batches_sent = get_total_batches_sent()
    total_batch_messages_sent = get_total_batch_messages_sent()

    return (
        "📊 **ʙᴏᴛ sᴛᴀᴛs** 📊\n\n"
        f"👥 ᴛᴏᴛᴀʟ ᴜsᴇʀs: `{total_users}`\n"
        f"⭐ ᴘʀᴇᴍɪᴜᴍ ᴜsᴇʀs: `{premium_users}`\n"
        f"📁 ᴛᴏᴛᴀʟ ғɪʟᴇs sᴛᴏʀᴇᴅ: `{total_files_stored}`\n"
        f"📂 ғɪʟᴇs sᴇɴᴛ: `{total_files_sent}`\n"
        f"📦 ʙᴀᴛᴄʜᴇs sᴇɴᴛ: `{total_batches_sent}`\n"
        f"🗂️ ʙᴀᴛᴄʜ ᴍᴇssᴀɢᴇs sᴇɴᴛ: `{total_batch_messages_sent}`"
    )


def get_main_buttons():
    return InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("• 🆓 ғʀᴇᴇ ᴜsᴇʀs •", callback_data="show_free_users_0")],
            [InlineKeyboardButton("• ⭐ ᴘʀᴇᴍɪᴜᴍ ᴜsᴇʀs •", callback_data="show_premium_users_0")],
            [InlineKeyboardButton("• ✖️ ᴄʟᴏsᴇ •", callback_data="close_stats")],
        ]
    )


def get_list_buttons(current_page, total_pages, prefix):
    buttons = []

    nav_buttons = []
    if current_page > 0:
        nav_buttons.append(InlineKeyboardButton("⏮ Back", callback_data=f"{prefix}_{current_page-1}"))
    if current_page < total_pages - 1:
        nav_buttons.append(InlineKeyboardButton("⏭ Next", callback_data=f"{prefix}_{current_page+1}"))

    if nav_buttons:
        buttons.append(nav_buttons)

    buttons.append([
        InlineKeyboardButton("• 🔙 ʙᴀᴄᴋ •", callback_data="back_stats"),
        InlineKeyboardButton("• ✖️ ᴄʟᴏsᴇ •", callback_data="close_stats")
    ])
    return InlineKeyboardMarkup(buttons)


def get_user_list(users, page):
    start = page * PER_PAGE
    end = start + PER_PAGE
    user_ids = [str(user["_id"]) for user in users[start:end]]
    return "\n".join(user_ids)


from pyrogram import Client, filters

@Client.on_message(filters.command("stats"))
async def stats_handler(client, message):
    try:
        log.info(f"👑 ADMINS list: {ADMINS}, User ID: {message.from_user.id}")
        # Check if user is admin
        if message.from_user.id not in ADMINS:
            return await message.reply_text("❌ You need admin access to use this command.")

        # Normal stats logic for admins
        await message.reply_text(get_stats_text(), reply_markup=get_main_buttons())

    except Exception as e:
        log.exception(f"🔥 Error in /stats handler: {e}")
        await message.reply_text("⚠️ Failed to fetch stats. Please try again later.")


async def show_users_list(query, prefix, users):
    total_pages = (len(users) + PER_PAGE - 1) // PER_PAGE
    page = int(query.data.split("_")[-1])
    text = f"**{prefix.replace('_',' ').title()} List**\n\n" + get_user_list(users, page)
    await query.message.edit_text(text, reply_markup=get_list_buttons(page, total_pages, prefix))
	
	
	
	
	
    
    
@Client.on_callback_query(filters.regex(r"show_free_users_\d+"))
async def show_free_users(client, query):
    users = list(users_col.find({
        "$or": [
            {"premium_until": {"$exists": False}},
            {"premium_until": {"$lte": datetime.datetime.utcnow()}}
        ]
    }))

    if not users:
        await query.message.edit_text("🆓 No free users found.", reply_markup=get_back_buttons())
        return

    await show_users_list(query, "free_users", users)


@Client.on_callback_query(filters.regex(r"show_premium_users_\d+"))
async def show_premium_users(client, query):
     
         

    now = datetime.datetime.utcnow()
    users = list(users_col.find({"premium_until": {"$gt": now}}))

    if not users:
        await query.message.edit_text("⭐ No premium users found.", reply_markup=get_back_buttons())
        return

    await show_users_list(query, "premium_users", users)


@Client.on_callback_query(filters.regex("back_stats"))
async def back_stats(client, query):
     
         

    await query.message.edit_text(get_stats_text(), reply_markup=get_main_buttons())


@Client.on_callback_query(filters.regex("close_stats"))
async def close_stats(client, query):
     
         

    await query.message.delete()


def get_back_buttons():
    return InlineKeyboardMarkup(
        [[
            InlineKeyboardButton("• 🔙 ʙᴀᴄᴋ •", callback_data="back_stats"),
            InlineKeyboardButton("• ✖️ ᴄʟᴏsᴇ •", callback_data="close_stats")
        ]]
    )

