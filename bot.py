import asyncio
import random
import string
from datetime import datetime
from bson import ObjectId

from pyrogram import Client, filters
from pyrogram.errors import FloodWait, Forbidden
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

import config
import database as db

app = Client(
    "FileStoreBot",
    bot_token=config.BOT_TOKEN,
    api_id=config.API_ID,
    api_hash=config.API_HASH
)

# ------------- Helpers -------------

def make_verify_slug():
    # 30 random chars AFTER prefix
    rand = "".join(random.choices(string.ascii_lowercase + string.digits, k=config.VERIFY_SLUG_RANDOM_LEN))
    return f"verify_{rand}"

def bot_deeplink(slug_or_param: str):
    # t.me/<username>?start=<param>
    # We don't know username yet here—get at runtime
    # (We'll call get_me() each time we need to build it)
    return slug_or_param

async def shorten_url(full_start_param: str):
    """
    Build a deep link and (optionally) shorten it via your shortener API.
    If shortener creds aren't set, falls back to native t.me link.
    """
    me = await app.get_me()
    deeplink = f"https://t.me/{me.username}?start={full_start_param}"

    # If no shortener configured, return t.me link
    if not config.SHORTENER_API_BASE or not config.SHORTENER_API_KEY:
        return deeplink

    # Example stub — adjust to your shortener's API spec.
    # Since we cannot make external requests here, we just return deeplink.
    # Replace with real API call when deploying (requests.post to your service).
    try:
        # TODO: integrate actual shortener API here.
        # Example pseudo:
        # r = requests.post(f"{config.SHORTENER_API_BASE}/shorten", data={"key": config.SHORTENER_API_KEY, "url": deeplink})
        # short = r.json().get("shortenedUrl", deeplink)
        short = deeplink
        return short
    except Exception:
        return deeplink

async def send_file_by_dbid(chat_id, file_db_id, caption=None):
    file_doc = db.get_file_by_dbid(file_db_id)
    if not file_doc:
        return await app.send_message(chat_id, "❌ File not found or removed.")
    await app.send_cached_media(
        chat_id=chat_id,
        file_id=file_doc["file_id"],
        caption=caption or f"📂 {file_doc.get('file_name', '')}".strip()
    )

# ------------- Commands -------------

@app.on_message(filters.command("start") & filters.private)
async def start(_, message):
    user = db.ensure_user(message.from_user.id, message.from_user.first_name or "")
    args = message.command[1:] if len(message.command) > 1 else []

    # Case A: verify slug flow
    if args and args[0].startswith("verify_"):
        slug = args[0]
        file_db_id, status = db.consume_verification(slug, message.from_user.id)
        if status == "not_found":
            return await message.reply_text("❌ Invalid or unknown verification link.")
        if status == "expired":
            return await message.reply_text("⌛ This verification link expired. Please request a new one.")
        if status == "wrong_user":
            return await message.reply_text("⚠️ This verification link is bound to a different user.")
        # status ok or already_consumed → still grant (idempotent) and send file
        new_until = db.add_premium_hours(message.from_user.id, config.VERIFY_PREMIUM_HOURS)
        await message.reply_text(
            f"✅ Verification complete! You’ve been granted **{config.VERIFY_PREMIUM_HOURS} hours** of premium.\n"
            f"🕒 Premium until: `{new_until}`"
        )
        if file_db_id:
            await send_file_by_dbid(message.chat.id, file_db_id)
        return

    # Case B: file deep-link flow (param is a Mongo _id)
    if args:
        requested_id = args[0]
        # Check premium
        premium, until = db.is_premium(message.from_user.id)
        if config.PREMIUM_BYPASS and premium:
            await send_file_by_dbid(message.chat.id, requested_id)
            return

        # Not premium → generate verification slug unique to this user+file
        slug = make_verify_slug()
        try:
            # Ensure requested_id is valid ObjectId & file exists
            file_exists = db.get_file_by_dbid(requested_id)
            if not file_exists:
                return await message.reply_text("❌ File not found or removed.")
        except Exception:
            return await message.reply_text("❌ Invalid file link.")

        db.create_verification(slug, message.from_user.id, requested_id)
        short = await shorten_url(slug)

        btn = InlineKeyboardMarkup([
            [InlineKeyboardButton("✅ Verify & Unlock (8 hours)", url=short)],
        ])
        await message.reply_text(
            "🔒 You don’t have premium yet.\n"
            "Tap **Verify & Unlock** to get **8 hours of premium** instantly, then the file will be available.\n\n"
            "After completing, you’ll be redirected back to this bot.",
            reply_markup=btn
        )
        return

    # Case C: plain /start
    await message.reply_text("Hi! Send me a file (admins), or use a link to get a file.")

# Save admin uploads
@app.on_message((filters.user(config.ADMINS)) & (filters.document | filters.video | filters.audio))
async def save_file_handler(_, message):
    media = message.document or message.video or message.audio
    file_id = media.file_id
    file_name = getattr(media, "file_name", None)
    file_size = getattr(media, "file_size", None)
    if message.video:
        file_type = "video"
    elif message.audio:
        file_type = "audio"
    else:
        file_type = "document"

    dbid = db.save_file(file_id, file_type, file_name, file_size)
    me = await app.get_me()
    link = f"https://t.me/{me.username}?start={dbid}"
    await message.reply_text(
        f"✅ Saved!\n"
        f"📎 **{file_name or file_type}**\n"
        f"🔗 Link: {link}"
    )

# Premium: user check
@app.on_message(filters.command("mypremium") & filters.private)
async def mypremium(_, message):
    prem, until = db.is_premium(message.from_user.id)
    if prem:
        await message.reply_text(f"🌟 You are **premium**.\n🕒 Until: `{until}`")
    else:
        if until:
            await message.reply_text("❌ Not premium (previous premium expired).")
        else:
            await message.reply_text("❌ Not premium.")

# Admin: add premium (days)
@app.on_message(filters.command("addpremium") & filters.user(config.ADMINS))
async def addpremium(_, message):
    # /addpremium user_id days
    parts = message.text.split()
    if len(parts) != 3:
        return await message.reply_text("Usage: `/addpremium user_id days`", quote=True)
    try:
        uid = int(parts[1])
        days = int(parts[2])
    except ValueError:
        return await message.reply_text("Provide integers: user_id and days.", quote=True)

    until = db.add_premium_days(uid, days)
    await message.reply_text(f"✅ Premium added.\n👤 User: `{uid}`\n🕒 Until: `{until}`")

# Admin: remove premium
@app.on_message(filters.command("removepremium") & filters.user(config.ADMINS))
async def removepremium(_, message):
    parts = message.text.split()
    if len(parts) != 2:
        return await message.reply_text("Usage: `/removepremium user_id`", quote=True)
    try:
        uid = int(parts[1])
    except ValueError:
        return await message.reply_text("Provide a valid user_id.", quote=True)

    db.remove_premium(uid)
    await message.reply_text(f"🗑️ Premium removed for `{uid}`.")

# Stats
@app.on_message(filters.command("stats") & filters.user(config.ADMINS))
async def stats(_, message):
    s = db.get_stats()
    text = (
        "📊 **Bot Statistics**\n\n"
        f"👤 Total Users: `{s['total_users']}`\n"
        f"📂 Total Files: `{s['total_files']}`\n"
    )
    if s["last_user"]:
        lu = s["last_user"]
        text += (
            f"🆕 Last User: `{lu.get('first_name','')}` (ID: `{lu.get('user_id')}`)\n"
            f"📅 Joined: `{lu.get('joined_at')}`\n"
        )
    await message.reply_text(text)

# ------------- Broadcast (background) -------------

async def run_broadcast(send_content):
    users_cur = db.users.find({})
    total = 0
    success = 0
    failed = 0

    for u in users_cur:
        total += 1
        uid = u["user_id"]
        try:
            if isinstance(send_content, str):
                await app.send_message(uid, send_content)
            else:
                await send_content.copy(uid)
            success += 1
        except FloodWait as e:
            await asyncio.sleep(e.value)
        except Forbidden:
            failed += 1
        except Exception:
            failed += 1

    result = (
        f"✅ Broadcast finished!\n\n"
        f"👥 Total Users: `{total}`\n"
        f"📩 Success: `{success}`\n"
        f"❌ Failed: `{failed}`"
    )
    for admin_id in config.ADMINS:
        try:
            await app.send_message(admin_id, result)
        except:
            pass

@app.on_message(filters.command("broadcast") & filters.user(config.ADMINS))
async def broadcast(_, message):
    if len(message.command) < 2 and not message.reply_to_message:
        return await message.reply_text("Use `/broadcast your_message` or reply to a message with `/broadcast`")

    if message.reply_to_message:
        send_content = message.reply_to_message
    else:
        send_content = message.text.split(None, 1)[1]

    await message.reply_text("📢 Broadcast started in background…")
    asyncio.create_task(run_broadcast(send_content))

# ------------- Runner -------------

print("Bot started…")
app.run()