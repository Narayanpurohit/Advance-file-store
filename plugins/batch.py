# batch.py
import logging
import random
import string
import asyncio
from pyrogram import Client, filters
from pyrogram.types import Message

from database import save_batch
from bot import get_admins, get_bool, get_str
from .ask import ask

log = logging.getLogger(__name__)
log.info("📍 batch.py loaded successfully")


# -------------------- Helpers --------------------
def generate_slug(length: int = 16):
    return "batch_" + ''.join(random.choices(string.ascii_letters + string.digits, k=length))


def extract_file_info(msg: Message):
    """
    Detect file type and extract file info for ANY supported message.
    Returns: file_id, file_type, file_name, file_size
    """
    # Document
    if msg.document:
        return msg.document.file_id, "doc", msg.document.file_name, msg.document.file_size

    # Video
    if msg.video:
        return msg.video.file_id, "vid", msg.video.file_name, msg.video.file_size

    # Audio
    if msg.audio:
        return msg.audio.file_id, "aud", msg.audio.file_name, msg.audio.file_size

    # Photo
    # Photo
    if msg.photo:
        return msg.photo.file_id, "pht", None, msg.photo.file_size
    # Animation
    if msg.animation:
        return msg.animation.file_id, "ani", msg.animation.file_name, msg.animation.file_size

    # Sticker
    if msg.sticker:
        return msg.sticker.file_id, "sti", None, None

    # Text message
    if msg.text:
        return None, "text", None, None

    return None, "unknown", None, None


# -------------------- /batch Command --------------------
@Client.on_message(filters.private & filters.command("batch"))
async def batch_handler(client: Client, message: Message):
    user_id = message.from_user.id

    ADMINS = get_admins()
    PUBLIC_BOT = get_bool("PUBLIC_BOT")
    DEKOY = get_bool("DEKOY")
    BOT_USERNAME = get_str("BOT_USERNAME")

    USERNAME = "Itadori101bot" if DEKOY else BOT_USERNAME

    # 🔒 Permission Check
    if not PUBLIC_BOT and user_id not in ADMINS:
        return await message.reply_text("❌ This bot only stores files. You can’t use /batch directly.")

    await message.reply_text(
        "📤 **Forward the first message** from your DB channel (with forward tag), "
        "or send the **message link**.\n\n⏱ Timeout: 2 minutes."
    )

    # ---------------- STEP 1: First Message ----------------
    while True:
        try:
            first = await ask(client, user_id, "➡️ Send the **first message** again:", 120)
        except asyncio.TimeoutError:
            return await client.send_message(user_id, "⏰ Timeout! Start again with /batch.")

        if first.forward_from_chat:
            chat_id = first.forward_from_chat.id
            first_msg_id = first.forward_from_message_id

        elif first.text and "/c/" in first.text:
            try:
                chat_id = int("-100" + first.text.split("/c/")[1].split("/")[0])
                first_msg_id = int(first.text.split("/")[-1])
            except:
                await first.reply_text("❌ Invalid first message link.")
                continue
        else:
            await first.reply_text("❌ Please forward a valid message or link.")
            continue
        break

    # ---------------- STEP 2: Last Message ----------------
    await message.reply_text(
        "📥 Now forward the **last message** (or link).\n⏱ Timeout: 2 minutes."
    )

    while True:
        try:
            last = await ask(client, user_id, "➡️ Send the **last message**:", 120)
        except asyncio.TimeoutError:
            return await client.send_message(user_id, "⏰ Timeout! Start again with /batch.")

        if last.forward_from_chat:
            last_chat_id = last.forward_from_chat.id
            last_msg_id = last.forward_from_message_id

        elif last.text and "/c/" in last.text:
            try:
                last_chat_id = int("-100" + last.text.split("/c/")[1].split("/")[0])
                last_msg_id = int(last.text.split("/")[-1])
            except:
                await last.reply_text("❌ Invalid last message link.")
                continue
        else:
            await last.reply_text("❌ Please forward a valid message or link.")
            continue

        if chat_id != last_chat_id:
            await last.reply_text("❌ Both messages must be from SAME channel.")
            continue

        if last_msg_id < first_msg_id:
            await last.reply_text("❌ Last message ID must be greater than first.")
            continue

        break

    # ---------------- STEP 3: Fetch Messages ----------------
    await client.send_message(user_id, "📦 Fetching messages... Please wait.")

    messages = []
    types_detected = set()

    for msg_id in range(first_msg_id, last_msg_id + 1):
        try:
            msg = await client.get_messages(chat_id, msg_id)
            if not msg:
                continue

            file_id, file_type, file_name, file_size = extract_file_info(msg)
            caption = msg.caption or msg.text or None

            types_detected.add(file_type)

            messages.append({
                "chat_id": chat_id,
                "message_id": msg.id,
                "file_id": file_id,
                "file_type": file_type,
                "file_name": file_name,
                "file_size": file_size,
                "caption": caption
            })

        except Exception as e:
            log.warning(f"Failed to fetch message {msg_id}: {e}")

    if not messages:
        return await client.send_message(user_id, "❌ No valid messages found in that range.")

    # Batch type detection
    batch_type = "mix" if len(types_detected) > 1 else list(types_detected)[0]

    # ---------------- STEP 4: Save Batch ----------------
    slug = generate_slug()

    success = save_batch(
        slug=slug,
        owner_id=user_id,
        channel_id=chat_id,
        msg_count=len(messages),
        batch_type=batch_type,
        is_premium=False,
        messages=messages
    )

    if success:
        await client.send_message(
            user_id,
            f"✅ **Batch created successfully!**\n\n"
            f"🔗 Link: https://t.me/{USERNAME}?start={slug}"
        )
    else:
        await client.send_message(user_id, "⚠️ Failed to save batch. Try again.")