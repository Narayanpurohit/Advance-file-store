import logging
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pymongo import MongoClient
import os

# ================== LOGGING ================== #
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - [%(levelname)s] - %(message)s"
)
logger = logging.getLogger(__name__)

# ================== CONFIG ================== #
BOT_TOKEN = os.getenv("BOT_TOKEN", "YOUR_BOT_TOKEN")

MONGO_URI = os.getenv("MONGO_URI", "YOUR_MONGO_URI")
mongo = MongoClient(MONGO_URI)
db = mongo["file_store"]

users_col = db["users"]     # db_code + bot username stored here
files_col = db["files"]     # file storage
stats_col = db["stats"]
batch_col = db["batches"]

# ================== BOT ================== #
app = Client("file_store_bot", bot_token=BOT_TOKEN)


# =======================================================
# 1️⃣  FUNCTION — Extract Bot Username using db_code
# =======================================================
def get_bot_username_by_dbcode(db_code: str):
    """
    Fetches bot username stored inside the 'users' DB collection.
    """
    logger.info(f"🔍 Looking up bot username for db_code={db_code}")

    data = users_col.find_one({"db_code": db_code})
    if not data:
        logger.error("❌ No bot found for this db_code!")
        return None

    bot_username = data.get("bot_username")
    logger.info(f"✔ Bot username found: {bot_username}")
    return bot_username


# =======================================================
# 2️⃣ SLUG EXTRACTOR FUNCTIONS
# =======================================================
def extract_file_type(full_slug: str):
    try:
        return full_slug.split("_")[0]  # vid, img, file
    except:
        return None

def extract_db_code(full_slug: str):
    try:
        return full_slug.split("_")[1]  # example: fzbot
    except:
        return None

def extract_core_slug(full_slug: str):
    """
    From: vid_fzbot_5q3szi5rp71w
    Returns: 5q3szi5rp71w
    """
    try:
        return full_slug.split("_", 2)[2]
    except:
        return None


# =======================================================
# 3️⃣ START HANDLER
# =======================================================
@app.on_message(filters.command("start"))
async def start_cmd(client, message):
    user_id = message.from_user.id

    # Check for deep link payload
    if len(message.command) > 1:
        payload = message.command[1]
        logger.info(f"📩 Received /start command with payload")
        logger.info(f"📦 Received payload: {payload}")

        file_type = extract_file_type(payload)
        db_code = extract_db_code(payload)
        core_slug = extract_core_slug(payload)

        logger.info(f"Parsed → type={file_type}, db_code={db_code}, slug={core_slug}")

        if not file_type or not db_code or not core_slug:
            return await message.reply("Invalid link format!")

        # Fetch bot username
        bot_username = get_bot_username_by_dbcode(db_code)
        if not bot_username:
            return await message.reply("Bot not found for this link.")

        logger.info(f"🔗 Generating deep link for bot: {bot_username}")

        # Lookup file from files_col
        logger.info("📄 Checking if file exists in DB...")
        file_data = files_col.find_one({"slug": core_slug})

        if not file_data:
            logger.error("❌ File not found in DB")
            return await message.reply("❌ File has expired or not found.")

        logger.info("✔ File found in DB.")

        file_name = file_data.get("file_name", "File")
        file_id = file_data.get("file_id")

        # Send file with button
        await message.reply(
            f"📁 **{file_name}**\nYour file is ready to download.",
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            "📥 Download File",
                            url=f"https://t.me/{bot_username}?start=get_{core_slug}"
                        )
                    ]
                ]
            )
        )
        return

    # Normal /start (without payload)
    await message.reply(
        "👋 Welcome!\nSend me any file and I will generate a shareable link."
    )


# =======================================================
# 4️⃣ DEFAULT FILE HANDLER — STORE FILE & GENERATE SLUG
# =======================================================
import random
import string

def generate_slug():
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=12))


@app.on_message(filters.document | filters.video | filters.audio)
async def save_file(client, message):
    file = message.document or message.video or message.audio

    slug = generate_slug()
    file_type = "vid" if message.video else "file"

    # Create slug format: type_dbcode_slug
    # IMPORTANT: You MUST store db_code for this bot in users_col

    data = users_col.find_one({"bot_username": (await app.get_me()).username})

    if not data:
        return await message.reply("❌ Bot is not registered in DB.")

    db_code = data.get("db_code")

    final_slug = f"{file_type}_{db_code}_{slug}"

    files_col.insert_one({
        "slug": slug,
        "full_slug": final_slug,
        "file_id": file.file_id,
        "file_name": file.file_name or "File",
        "user_id": message.from_user.id
    })

    await message.reply(
        "✅ File saved!\n"
        f"📎 Your link:\n\n"
        f"https://t.me/{(await app.get_me()).username}?start={final_slug}"
    )


# =======================================================
# RUN BOT
# =======================================================
app.run()