import os
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

log.info("🔥 Starting Mediator Bot initialization...")


# ---------------------------------------------------------
# Bot Config
# ---------------------------------------------------------
API_ID = 15191874
API_HASH = "3037d39233c6fad9b80d83bb8a339a07"
BOT_TOKEN = "6723725173:AAGjp4K-YY3L9eQIjHHBSWBjN586FA4Trtk"

MONGO_URL = "mongodb+srv://hp108044:zWy9AuflXmsrAfSY@cluster0.zlecn7m.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
DB_NAME = "clone_maker"

log.info(f"🔧 Loaded API config. DB={DB_NAME}")


# ---------------------------------------------------------
# Pyrogram Client
# ---------------------------------------------------------
app = Client(
    "MediatorBot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)
log.info("🤖 Pyrogram Client created.")


# ---------------------------------------------------------
# MongoDB Setup
# ---------------------------------------------------------
mongo = MongoClient(MONGO_URL)
db = mongo[DB_NAME]

log.info("🗄 Connected to MongoDB.")

files_col = db.files
batches_col = db.batches
bots_col = db.users   # unchanged

log.info("📦 Collections mapped: files, batches, users")


# ---------------------------------------------------------
# Function: Get bot username from db-code
# ---------------------------------------------------------
def get_BOT_USERNAME_by_code(db_code: str):
    log.info(f"🔍 Looking up bot username for db_code={db_code}")

    bot = bots_col.find_one({"DB_NAME": db_code})

    if bot:
        log.info(f"✔ Bot username found: {bot.get('BOT_USERNAME')}")
    else:
        log.error("❌ Bot username NOT FOUND in DB!")

    return bot["BOT_USERNAME"] if bot else None


# ---------------------------------------------------------
# START Handler
# ---------------------------------------------------------
@app.on_message(filters.command("start"))
async def start_handler(client, message):

    log.info("📩 Received /start command")

    # ------------------------------
    # Normal /start
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
        payload = message.command[1]
        log.info(f"📦 Received payload: {payload}")

        link_type, dbcode, slug = payload.split("_", 2)

        db2 = mongo[dbcode]
        files_col = db2.files
        batches_col = db2.batches

        log.info(f"Parsed → type={link_type}, db_code={dbcode}, slug={slug}")

    except Exception as e:
        log.error(f"❌ Payload parsing failed: {e}")
        return await message.reply(
            "❌ Invalid link format.\n\nExpected: `type_dbcode_slug`"
        )

    # ------------------------------
    # Fetch bot username
    # ------------------------------
    BOT_USERNAME = get_BOT_USERNAME_by_code(dbcode)

    if not BOT_USERNAME:
        return await message.reply("❌ db-code not found. Bot username missing!")

    # ------------------------------
    # Batch Type
    # ------------------------------
    if link_type.lower() == "batch":
        log.info("📁 Link detected as BATCH. Fetching batch from DB...")

        batch = batches_col.find_one({
            "$or": [
                {"slug": slug},
                {"slug2": slug}
            ]
        })

        if not batch:
            return await message.reply("❌ Batch not found!")

        real_slug = batch["slug"]

        deep_link = f"https://t.me/{BOT_USERNAME}?start={real_slug}"

        btn = InlineKeyboardMarkup(
            [[InlineKeyboardButton("• ɢᴇᴛ ʙᴀᴛᴄʜ •", url=deep_link)]]
        )

        text = (
            f"📦 **Batch Details**\n"
            f"**• Messages**: `{batch['msg_count']}`\n"
            f"**• Type**: `{batch['type']}`"
        )

        return await message.reply(text, reply_markup=btn)

    # ------------------------------
    # File Type
    # ------------------------------
    else:
        log.info("📄 Link detected as FILE. Fetching file from DB...")

        file = files_col.find_one({
            "$or": [
                {"slug": slug},
                {"slug2": slug}
            ]
        })

        if not file:
            return await message.reply("❌ File not found!")

        real_slug = file["slug"]

        deep_link = f"https://t.me/{BOT_USERNAME}?start={real_slug}"

        btn = InlineKeyboardMarkup(
            [[InlineKeyboardButton("• ɢᴇᴛ ғɪʟᴇ •", url=deep_link)]]
        )

        text = (
            f"📁 **File Details**\n"
            f"**• Name**: `{file['file_name']}`\n"
            f"**• Size**: `{file['file_size']}`\n"
            f"**• Type**: `{file['file_type']}`"
        )

        return await message.reply(text, reply_markup=btn)


# ---------------------------------------------------------
# Run Bot
# ---------------------------------------------------------
log.info("🚀 Mediator Bot started and running!")
app.run()