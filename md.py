import logging
from datetime import datetime
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pymongo import MongoClient


# ---------------------------------------------------------
# Logging Setup
# ---------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - [%(levelname)s] - %(message)s"
)
log = logging.getLogger("MediatorBot")


# ---------------------------------------------------------
# Bot Config
# ---------------------------------------------------------
API_ID = 12345
API_HASH = "your_api_hash"
BOT_TOKEN = "your_bot_token"

MONGO_URL = "your_mongo_url"
DB_NAME = "mediator_database"

app = Client(
    "MediatorBot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)


# ---------------------------------------------------------
# MongoDB Setup
# ---------------------------------------------------------
mongo = MongoClient(MONGO_URL)
db = mongo[DB_NAME]

files_col = db.files        # file details
batches_col = db.batches    # batch details
bots_col = db.bots          # store bot username per db-code


# ---------------------------------------------------------
# Function: Get bot username from db-code
# ---------------------------------------------------------
def get_bot_username_by_code(db_code: str):
    """
    Fetch bot username using db-code.
    """
    bot = bots_col.find_one({"db_code": db_code})
    return bot["bot_username"] if bot else None


# ---------------------------------------------------------
# START Handler
# ---------------------------------------------------------
@app.on_message(filters.command("start"))
async def start_handler(client, message):

    # ------------------------------
    # Normal /start (no payload)
    # ------------------------------
    if len(message.command) == 1:
        return await message.reply(
            "👋 **Welcome to Mediator Bot**\n"
            "Send a valid mediated link to continue."
        )

    # ------------------------------
    # Start with payload
    # ------------------------------
    try:
        payload = message.command[1]  # link-type_db-code_slug
        link_type, db_code, slug = payload.split("_", 2)

    except:
        return await message.reply("❌ Invalid link format.\n\nExpected: `type_dbcode_slug`")

    log.info(f"Received start link: type={link_type}, db={db_code}, slug={slug}")

    # ------------------------------
    # Fetch bot username via db-code
    # ------------------------------
    bot_username = get_bot_username_by_code(db_code)

    if not bot_username:
        return await message.reply("❌ db-code not found. Bot username missing!")

    deep_link = f"https://t.me/{bot_username}?start={slug}"

    btn = InlineKeyboardMarkup(
        [[InlineKeyboardButton("🔗 Open in main bot", url=deep_link)]]
    )

    # ------------------------------
    # Batch Type
    # ------------------------------
    if link_type.lower() == "batch":

        batch = batches_col.find_one({"slug": slug})

        if not batch:
            return await message.reply("❌ Batch not found!")

        text = (
            f"📦 **Batch Details**\n"
            f"• Messages: `{batch['msg_count']}`\n"
            f"• Type: `{batch['type']}`\n"
            f"• Premium: `{batch['is_premium']}`\n"
            f"• Slug: `{slug}`"
        )

        return await message.reply(text, reply_markup=btn)

    # ------------------------------
    # File Type
    # ------------------------------
    else:
        file = files_col.find_one({"slug": slug})

        if not file:
            return await message.reply("❌ File not found!")

        text = (
            f"📁 **File Details**\n"
            f"• Name: `{file['file_name']}`\n"
            f"• Size: `{file['file_size']}`\n"
            f"• Type: `{file['file_type']}`\n"
            f"• Slug: `{slug}`"
        )

        return await message.reply(text, reply_markup=btn)


# ---------------------------------------------------------
# Run Bot
# ---------------------------------------------------------
log.info("🤖 Mediator Bot started!")
app.run()