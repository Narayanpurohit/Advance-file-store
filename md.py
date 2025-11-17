import logging
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pymongo import MongoClient
import random
import string

# ================== LOGGING ================== #
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - [%(levelname)s] - %(message)s"
)
logger = logging.getLogger("MediatorBot")
logger.info("🔥 Starting Mediator Bot...")

# ================== CONFIG ================== #
API_ID = 15191874
API_HASH = "3037d39233c6fad9b80d83bb8a339a07"
BOT_TOKEN = "6723725173:AAGjp4K-YY3L9eQIjHHBSWBjN586FA4Trtk"

MONGO_URI = "mongodb+srv://hp108044:zWy9AuflXmsrAfSY@cluster0.zlecn7m.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
DB_NAME = "clone_maker"

# ================== MONGO ================== #
mongo = MongoClient(MONGO_URI)
db = mongo[DB_NAME]

users_col = db["users"]      # db_code + bot_username
files_col = db["files"]      # file storage
stats_col = db["stats"]      # stats
batch_col = db["batches"]    # batch uploads

logger.info("🗄 Connected to MongoDB and collections mapped.")

# ================== PYROGRAM CLIENT ================== #
app = Client(
    "MediatorBot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)
logger.info("🤖 Pyrogram Client initialized.")

# ================== HELPER FUNCTIONS ================== #
def get_bot_username_by_dbcode(db_code: str):
    """Fetch bot username stored inside the 'users' collection."""
    logger.info(f"🔍 Looking up bot username for db_code={db_code}")
    data = users_col.find_one({"db_code": db_code})
    if not data:
        logger.error("❌ No bot found for this db_code!")
        return None
    bot_username = data.get("bot_username")
    logger.info(f"✔ Bot username found: {bot_username}")
    return bot_username

def extract_file_type(full_slug: str):
    try:
        return full_slug.split("_")[0]  # vid, doc, etc.
    except:
        return None

def extract_db_code(full_slug: str):
    try:
        return full_slug.split("_")[1]  # db code
    except:
        return None

def extract_core_slug(full_slug: str):
    """Extract core slug from full_slug like vid_fzbot_5q3szi5rp71w → 5q3szi5rp71w"""
    try:
        return full_slug.split("_", 2)[2]
    except:
        return None

def generate_slug():
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=12))

# ================== START HANDLER ================== #
@app.on_message(filters.command("start") & filters.private)
async def start_handler(client, message):
    user_id = message.from_user.id

    if len(message.command) == 1:
        logger.info(f"📩 Normal /start from user {user_id}")
        return await message.reply(
            "👋 **Welcome to Mediator Bot**\n"
            "Send a valid mediated link to continue."
        )

    # Payload mode
    payload = message.command[1]
    logger.info(f"📩 /start with payload: {payload}")

    file_type = extract_file_type(payload)
    db_code = extract_db_code(payload)
    core_slug = extract_core_slug(payload)

    logger.info(f"Parsed payload → type={file_type}, db_code={db_code}, slug={core_slug}")

    if not file_type or not db_code or not core_slug:
        logger.error("❌ Payload parsing failed")
        return await message.reply("❌ Invalid link format!")

    # Get bot username
    bot_username = get_bot_username_by_dbcode(db_code)
    if not bot_username:
        return await message.reply("❌ Bot not found for this link.")

    logger.info(f"🔗 Generating deep link: {bot_username}")
    deep_link = f"https://t.me/{bot_username}?start={payload}"

    btn = InlineKeyboardMarkup([[InlineKeyboardButton("🔗 Open in main bot", url=deep_link)]])
    logger.info("🧩 Inline button created.")

    # Check if batch or file
    if file_type.lower() == "batch":
        logger.info("📁 Payload is a batch, fetching batch data...")
        batch_data = batch_col.find_one({"slug": core_slug})
        if not batch_data:
            logger.error("❌ Batch not found in DB")
            return await message.reply("❌ Batch not found!")

        text = (
            f"📦 **Batch Details**\n"
            f"• Messages: `{batch_data['msg_count']}`\n"
            f"• Type: `{batch_data['type']}`\n"
            f"• Premium: `{batch_data['is_premium']}`\n"
            f"• Slug: `{core_slug}`"
        )
        return await message.reply(text, reply_markup=btn)

    else:
        logger.info("📄 Payload is a file, fetching file data...")
        file_data = files_col.find_one({"slug": core_slug})
        if not file_data:
            logger.error("❌ File not found in DB")
            return await message.reply("❌ File not found!")

        text = (
            f"📁 **File Details**\n"
            f"• Name: `{file_data.get('file_name', 'Unknown')}`\n"
            f"• Size: `{file_data.get('file_size', 0)}`\n"
            f"• Type: `{file_data.get('file_type', 'Unknown')}`\n"
            f"• Slug: `{core_slug}`"
        )
        return await message.reply(text, reply_markup=btn)

# ================== SAVE FILE HANDLER ================== #
@app.on_message(filters.document | filters.video | filters.audio)
async def save_file(client, message):
    file_obj = message.document or message.video or message.audio
    user_id = message.from_user.id

    slug = generate_slug()
    file_type = "vid" if message.video else "doc"

    # Get db_code for this bot
    bot_info = await client.get_me()
    bot_data = users_col.find_one({"bot_username": bot_info.username})
    if not bot_data:
        return await message.reply("❌ Bot is not registered in DB.")
    db_code = bot_data.get("db_code")

    full_slug = f"{file_type}_{db_code}_{slug}"

    files_col.insert_one({
        "slug": slug,
        "full_slug": full_slug,
        "file_id": file_obj.file_id,
        "file_name": file_obj.file_name or "File",
        "file_size": getattr(file_obj, "file_size", 0),
        "file_type": file_type,
        "user_id": user_id
    })

    await message.reply(
        f"✅ File saved!\nYour link:\nhttps://t.me/{bot_info.username}?start={full_slug}"
    )
    logger.info(f"✅ File stored for user {user_id} → {full_slug}")

# ================== RUN BOT ================== #
logger.info("🚀 Mediator Bot started and running!")
app.run()