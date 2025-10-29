import asyncio
import logging
import random
import string
from pyrogram import Client, filters
from database import save_batch
from bot import get_admins, get_bool

log = logging.getLogger(__name__)

# Store user state
batch_states = {}

def generate_slug(length: int = 16) -> str:
    """Generate a unique random slug."""
    return "batch_" + ''.join(random.choices(string.ascii_letters + string.digits, k=length))


@Client.on_message(filters.command("batch") & filters.private)
async def batch_handler(client, message):
    """Start batch creation (step 1)."""
    user_id = message.from_user.id
    ADMINS = get_admins()
    PUBLIC_BOT = get_bool("PUBLIC_BOT")

    if not PUBLIC_BOT and user_id not in ADMINS:
        return await message.reply_text("❌ This bot only stores files. You can’t use /batch directly.")

    if user_id in batch_states:
        return await message.reply_text("⚠️ You’re already creating a batch. Please finish or wait for timeout.")

    # Step 1 prompt
    await message.reply_text(
        "📤 **Forward the first message** from your batch channel (with forward tag),\n"
        "or send the **message link** here.\n\n⏱ You have 2 minutes."
    )

    # Set state
    batch_states[user_id] = {"step": "first", "first_msg": None}
    await asyncio.sleep(120)
    if user_id in batch_states and batch_states[user_id]["step"] == "first":
        batch_states.pop(user_id, None)
        await client.send_message(user_id, "⏰ Timeout! Please start again with /batch.")


@Client.on_message(filters.private & ~filters.command("batch"))
async def batch_message_listener(client, message):
    """Handles replies for batch steps."""
    user_id = message.from_user.id
    if user_id not in batch_states:
        return  # Not in batch creation flow

    try:
        state = batch_states[user_id]

        # Step 1: Capture first message
        if state["step"] == "first":
            if message.forward_from_chat:
                chat_id = message.forward_from_chat.id
                first_msg_id = message.forward_from_message_id
            elif message.text and "/c/" in message.text:
                try:
                    chat_id = int("-100" + message.text.split("/c/")[1].split("/")[0])
                    first_msg_id = int(message.text.split("/")[-1])
                except Exception:
                    return await message.reply_text("❌ Invalid first message link provided.")
            else:
                return await message.reply_text("❌ Please forward a valid message or send a proper link.")

            state.update({"step": "last", "chat_id": chat_id, "first_msg_id": first_msg_id})
            await message.reply_text(
                "📥 Great! Now forward the **last message** from your batch channel (with forward tag),\n"
                "or send its **message link**.\n\n⏱ You have 2 minutes."
            )

            await asyncio.sleep(120)
            if user_id in batch_states and batch_states[user_id]["step"] == "last":
                batch_states.pop(user_id, None)
                await client.send_message(user_id, "⏰ Timeout! Please start again with /batch.")
            return

        # Step 2: Capture last message
        elif state["step"] == "last":
            if message.forward_from_chat:
                last_chat_id = message.forward_from_chat.id
                last_msg_id = message.forward_from_message_id
            elif message.text and "/c/" in message.text:
                try:
                    last_chat_id = int("-100" + message.text.split("/c/")[1].split("/")[0])
                    last_msg_id = int(message.text.split("/")[-1])
                except Exception:
                    return await message.reply_text("❌ Invalid last message link provided.")
            else:
                return await message.reply_text("❌ Please forward a valid message or send a proper link.")

            chat_id = state["chat_id"]
            first_msg_id = state["first_msg_id"]

            # Validation
            if chat_id != last_chat_id:
                batch_states.pop(user_id, None)
                return await message.reply_text("❌ Both messages must be from the same channel.")
            if last_msg_id < first_msg_id:
                batch_states.pop(user_id, None)
                return await message.reply_text("❌ Last message ID must be greater than first.")

            # Fetch messages
            messages = []
            for msg_id in range(first_msg_id, last_msg_id + 1):
                try:
                    msg = await client.get_messages(chat_id, msg_id)
                    if msg:
                        messages.append({"chat_id": chat_id, "message_id": msg.id})
                except Exception as e:
                    log.warning(f"Failed to fetch message {msg_id}: {e}")

            if not messages:
                batch_states.pop(user_id, None)
                return await message.reply_text("❌ No valid messages found in that range.")

            slug = generate_slug()
            if save_batch(slug, messages):
                await message.reply_text(
                    f"✅ **Batch created successfully!**\n\n"
                    f"🔗 Link: https://t.me/{client.me.username}?start={slug}"
                )
            else:
                await message.reply_text("⚠️ Failed to save batch. Please try again.")

            batch_states.pop(user_id, None)

    except Exception as e:
        batch_states.pop(user_id, None)
        log.exception(f"Batch creation error for user {user_id}: {e}")
        await message.reply_text(f"⚠️ Error: {e}")