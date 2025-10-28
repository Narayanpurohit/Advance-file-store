import logging
import random
import string
from pyrogram import Client, filters
from database import save_batch
from bot import get_admins, get_bool
import asyncio

log = logging.getLogger(__name__)

# Track user states for batch creation
batch_states = {}  # {user_id: {"step": 1 or 2, "first_msg": {...}, "timeout_task": task}}

def generate_slug(length: int = 16) -> str:
    """Generate a unique random slug."""
    return "batch_" + ''.join(random.choices(string.ascii_letters + string.digits, k=length))

@Client.on_message(filters.command("batch") & filters.private)
async def batch_start(client, message):
    user_id = message.from_user.id
    ADMINS = get_admins()
    PUBLIC_BOT = get_bool("PUBLIC_BOT")

    # Access control
    if not PUBLIC_BOT and user_id not in ADMINS:
        return await message.reply_text("❌ Don't send messages directly — this bot only stores files.")

    # Initialize state for the user
    batch_states[user_id] = {"step": 1, "first_msg": None}

    # Ask for first message
    await message.reply_text(
        "📤 **Forward the first message** from your batch channel (with forward tag),\n"
        "or send the **message link** here.\n"
        "⏱ Timeout: 2 minutes"
    )

    # Set timeout to clear state
    batch_states[user_id]["timeout_task"] = asyncio.create_task(batch_timeout(client, user_id, 120))


async def batch_timeout(client, user_id, delay):
    await asyncio.sleep(delay)
    if user_id in batch_states:
        batch_states.pop(user_id)
        await client.send_message(user_id, "⏰ Batch creation timed out. Please start again with /batch.")


@Client.on_message(filters.private)
async def batch_message_listener(client, message):
    user_id = message.from_user.id

    if user_id not in batch_states:
        return  # User not in batch creation mode

    state = batch_states[user_id]

    try:
        # Parse forwarded message or link
        if state["step"] == 1:
            # First message
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
                return await message.reply_text("❌ Please forward a valid message or send a proper message link.")

            state["first_msg"] = {"chat_id": chat_id, "first_msg_id": first_msg_id}
            state["step"] = 2

            # Ask for last message
            await message.reply_text(
                "📤 **Now forward the last message** from your batch channel (with forward tag),\n"
                "or send its **message link** here.\n"
                "⏱ Timeout: 2 minutes"
            )

            # Reset timeout
            state["timeout_task"].cancel()
            state["timeout_task"] = asyncio.create_task(batch_timeout(client, user_id, 120))

        elif state["step"] == 2:
            # Last message
            first_msg = state["first_msg"]
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
                return await message.reply_text("❌ Please forward a valid message or send a proper message link.")

            # Validate same chat
            if first_msg["chat_id"] != last_chat_id:
                batch_states.pop(user_id)
                return await message.reply_text("❌ Both messages must be from the same channel.")

            if last_msg_id < first_msg["first_msg_id"]:
                batch_states.pop(user_id)
                return await message.reply_text("❌ Last message ID must be greater than the first one.")

            # Fetch messages
            messages = []
            for msg_id in range(first_msg["first_msg_id"], last_msg_id + 1):
                try:
                    msg = await client.get_messages(first_msg["chat_id"], msg_id)
                    if msg:
                        messages.append({"chat_id": first_msg["chat_id"], "message_id": msg.id})
                except Exception as e:
                    log.warning(f"Failed to fetch message {msg_id}: {e}")

            if not messages:
                batch_states.pop(user_id)
                return await message.reply_text("❌ No valid messages found in that range.")

            slug = generate_slug()
            if save_batch(slug, messages):
                await message.reply_text(
                    f"✅ **Batch created successfully!**\n\n"
                    f"🔗 Link: https://t.me/{client.me.username}?start={slug}"
                )
            else:
                await message.reply_text("⚠️ Failed to save batch. Please try again.")

            # Cleanup
            state["timeout_task"].cancel()
            batch_states.pop(user_id)

    except Exception as e:
        log.exception(f"Error during batch creation for user {user_id}: {e}")
        batch_states.pop(user_id)
        await message.reply_text(f"⚠️ Unexpected error: {e}")