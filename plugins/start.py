import os
import secrets
import logging
import requests
from pyrogram import Client, filters
from config import (
    VERIFICATION_MODE,
    VERIFY_SLUG_TTL_HOURS,
    SHORTENER_API_KEY,
    SHORTENER_API_BASE,
    CAPTION
)
from database import user_exists, add_user # your MongoDB helper functions
from utils import human_readable_size

log = logging.getLogger(__name__)


def shorten_url(long_url: str) -> str:
    """
    Shortens a URL using the Shareus API (or similar).
    """
    try:
        api_url = f"{SHORTENER_API_BASE}?key={SHORTENER_API_KEY}&link={long_url}"
        r = requests.get(api_url, timeout=10)
        if r.status_code == 200:
            return r.text.strip()
        else:
            log.error(f"Shortener API returned status {r.status_code}: {r.text}")
            return long_url
    except Exception as e:
        log.error(f"Error shortening URL: {e}")
        return long_url


@Client.on_message(filters.command("start") & filters.private)
async def start_handler(client, message):
    user_id = message.from_user.id
    args = message.text.split()

    # New user? Add to DB
    if not user_exists(user_id):
        add_user(user_id)
        log.info(f"New user {user_id} added to database.")

    # If only /start (no args)
    if len(args) == 1:
        await message.reply_text("👋 Welcome! Send me a file to get started.")
        return

    slug = args[1]

    # Check if it's a verification slug
    if slug.startswith("verify_"):
        if db.is_verification_valid(user_id, slug):
            db.upgrade_to_premium(user_id, hours=8)
            db.remove_verification_slug(user_id, slug)
            await message.reply_text("✅ Verified! You now have 8 hours of premium access.")
        else:
            await message.reply_text("❌ Verification link expired or invalid.")
        return

    # Otherwise, it's a file slug
    file_data = db.get_file_by_slug(slug)
    if not file_data:
        await message.reply_text("❌ File not found or has been removed.")
        return

    # Premium check
    if VERIFICATION_MODE and not db.is_premium(user_id):
        # Generate verification slug
        verify_slug = "verify_" + secrets.token_urlsafe(22)[:30]
        db.save_verification_slug(user_id, verify_slug, expiry_hours=VERIFY_SLUG_TTL_HOURS)
        long_url = f"https://t.me/{(await client.get_me()).username}?start={verify_slug}"
        short_url = shorten_url(long_url)
        await message.reply_text(
            f"🔑 Please verify to access this file:\n{short_url}"
        )
        return

    # Prepare caption
    file_name = file_data.get("file_name", "")
    file_size = file_data.get("file_size", 0)
    orig_caption = file_data.get("caption", "")

    caption_text = CAPTION.format(
        filename=file_name,
        filesize=human_readable_size(file_size),
        caption=orig_caption
    )

    # Send file based on type
    file_type = file_data.get("file_type")
    file_id = file_data.get("file_id")

    if file_type == "doc":
        await message.reply_document(file_id, caption=caption_text)
    elif file_type == "vid":
        await message.reply_video(file_id, caption=caption_text)
    elif file_type == "aud":
        await message.reply_audio(file_id, caption=caption_text)
    else:
        await message.reply_text("❌ Unknown file type.")

    # Update total file send counter
    db.increment_file_send_count()