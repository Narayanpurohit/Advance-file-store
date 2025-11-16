# batch.py
import logging
import random
import string
import asyncio
from pyrogram import Client, filters
from pyrogram.types import Message

from database import save_batch
from bot import get_admins, get_bool,get_str
from .ask import ask  # import the helper from ask.py

log = logging.getLogger(__name__)
log.info("📍 batch.py loaded successfully")


# -------------------- Helpers --------------------
def generate_slug(length: int = 16):
    """Generate a unique slug for identifying each batch."""
    return "batch_" + "{DB_NAME}_" + ''.join(random.choices(string.ascii_letters + string.digits, k=length))


# -------------------- /batch Command --------------------
@Client.on_message(filters.private & filters.command("batch"))
async def batch_handler(client: Client, message: Message):
    user_id = message.from_user.id
    ADMINS = get_admins()
    PUBLIC_BOT = get_bool("PUBLIC_BOT")
    DEKOY = get_bool("DEKOY")
    BOT_USERNAME=get_str("BOT_USERNAME")
    DB_NAME= get_str("DB_NAME")
    USERNAME = "Itadori101bot" if DEKOY else BOT_USERNAME

    # --- Permission Check ---
    if not PUBLIC_BOT and user_id not in ADMINS:
        return await message.reply_text("❌ This bot only stores files. You can’t use /batch directly.")

    await message.reply_text(
        "📤 **Forward the first message** from your DB channel (with forward tag), "
        "or send the **message link**.\n\n⏱ Timeout: 2 minutes."
    )

    # --- Step 1: Get First Message ---
    while True:
        try:
            first = await ask(client, user_id, "➡️ Send the **first message** again if you haven’t yet:", 120)
        except asyncio.TimeoutError:
            return await client.send_message(user_id, "⏰ Timeout! Please start again with /batch.")

        # Forwarded message
        if first.forward_from_chat:
            chat_id = first.forward_from_chat.id
            first_msg_id = first.forward_from_message_id
        # Message link
        elif first.text and "/c/" in first.text:
            try:
                chat_id = int("-100" + first.text.split("/c/")[1].split("/")[0])
                first_msg_id = int(first.text.split("/")[-1])
            except Exception:
                await first.reply_text("❌ Invalid first message link. Try again.")
                continue
        else:
            await first.reply_text("❌ Please forward a valid message or send a proper link.")
            continue
        break

    # --- Step 2: Get Last Message ---
    await client.send_message(
        user_id,
        "📥 Now forward the **last message** from your DB channel (with forward tag),\n"
        "or send its **message link**.\n\n⏱ Timeout: 2 minutes."
    )

    while True:
        try:
            last = await ask(client, user_id, "➡️ Send the **last message**:", 120)
        except asyncio.TimeoutError:
            return await client.send_message(user_id, "⏰ Timeout! Please start again with /batch.")

        if last.forward_from_chat:
            last_chat_id = last.forward_from_chat.id
            last_msg_id = last.forward_from_message_id
        elif last.text and "/c/" in last.text:
            try:
                last_chat_id = int("-100" + last.text.split("/c/")[1].split("/")[0])
                last_msg_id = int(last.text.split("/")[-1])
            except Exception:
                await last.reply_text("❌ Invalid last message link. Try again.")
                continue
        else:
            await last.reply_text("❌ Please forward a valid message or send a proper link.")
            continue

        # Validation
        if chat_id != last_chat_id:
            await last.reply_text("❌ Both messages must be from the same channel.")
            continue
        if last_msg_id < first_msg_id:
            await last.reply_text("❌ Last message ID must be greater than first.")
            continue
        break

    # --- Step 3: Fetch Messages ---
    await client.send_message(user_id, "📦 Fetching messages... Please wait.")
    messages = []
    for msg_id in range(first_msg_id, last_msg_id + 1):
        try:
            msg = await client.get_messages(chat_id, msg_id)
            if msg:
                messages.append({"chat_id": chat_id, "message_id": msg.id})
        except Exception as e:
            log.warning(f"Failed to fetch message {msg_id}: {e}")

    if not messages:
        return await client.send_message(user_id, "❌ No valid messages found in that range.")

    # --- Step 4: Save Batch ---
    slug = generate_slug()
    success = save_batch(slug, messages)

    if success:
        await client.send_message(
            user_id,
            f"✅ **Batch created successfully!**\n\n"
            f"🔗 Link: https://t.me/{USERNAME}?start={slug}"
        )
    else:
        await client.send_message(user_id, "⚠️ Failed to save batch. Please try again.")