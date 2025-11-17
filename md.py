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
API_ID = 15191874
API_HASH = "3037d39233c6fad9b80d83bb8a339a07"
BOT_TOKEN = "6723725173:AAGjp4K-YY3L9eQIjHHBSWBjN586FA4Trtk"


MONGO_URL =  "mongodb+srv://hp108044:zWy9AuflXmsrAfSY@cluster0.zlecn7m.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
DB_NAME = "clone_maker"




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
bots_col = db.users          # store bot username per db-code


# ---------------------------------------------------------
# Function: Get bot username from db-code
# ---------------------------------------------------------
def get_BOT_USERNAME_by_code(DB_NAME: str):
    """
    Fetch bot username using db-code.
    """
    bot = bots_col.find_one({"DB_NAME": DB_NAME})
    return bot["BOT_USERNAME"] if bot else None


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
        link_type, DB_NAME, slug = payload.split("_", 2)

    except:
        return await message.reply("❌ Invalid link format.\n\nExpected: `type_dbcode_slug`")

    log.info(f"Received start link: type={link_type}, db={DB_NAME}, slug={slug}")

    # ------------------------------
    # Fetch bot username via db-code
    # ------------------------------
    BOT_USERNAME = get_BOT_USERNAME_by_code(DB_NAME)

    if not BOT_USERNAME:
        return await message.reply("❌ db-code not found. Bot username missing!")

    deep_link = f"https://t.me/{BOT_USERNAME}?start={slug}"

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