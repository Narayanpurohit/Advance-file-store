import logging
import random
import string
from pyrogram import Client, filters
from pyromod import listen
from database import save_batch
from bot import get_admins, get_bool

log = logging.getLogger(__name__)

def generate_slug(length: int = 16) -> str:
    """Generate a unique random slug."""
    return "batch_" + ''.join(random.choices(string.ascii_letters + string.digits, k=length))

@Client.on_message(filters.command("batch") & filters.private)
async def batch_handler(client, message):
    user_id = message.from_user.id
    ADMINS = get_admins()
    PUBLIC_BOT = get_bool("PUBLIC_BOT")

    # Access control
    if not PUBLIC_BOT and user_id not in ADMINS:
        return await message.reply_text("❌ Don't send messages directly — this bot only stores files.")

    try:
        # Step 1: Ask for first message
        ask1 = await message.reply_text(
            "📤 **Forward the first message** from your batch channel (with forward tag),\n"
            "or send the **message link** here."
        )

        try:
            first_msg = await client.listen(message.chat.id, timeout=120)
        except Exception:
            await ask1.delete()
            return await message.reply_text("❌ Timeout: You did not reply within 2 minutes.")

        # Determine first message details
        if first_msg.forward_from_chat:
            chat_id = first_msg.forward_from_chat.id
            first_msg_id = first_msg.forward_from_message_id
        elif first_msg.text and "/c/" in first_msg.text:
            try:
                chat_id = int("-100" + first_msg.text.split("/c/")[1].split("/")[0])
                first_msg_id = int(first_msg.text.split("/")[-1])
            except Exception:
                await message.reply_text("❌ Invalid first message link provided.")
                return
        else:
            await message.reply_text("❌ Please forward a valid message or send a proper message link.")
            return

        await ask1.delete()
        await first_msg.delete()

        # Step 2: Ask for last message
        ask2 = await message.reply_text(
            "📤 **Now forward the last message** from your batch channel (with forward tag),\n"
            "or send its **message link**."
        )

        try:
            last_msg = await client.listen(message.chat.id, timeout=120)
        except Exception:
            await ask2.delete()
            return await message.reply_text("❌ Timeout: You did not reply within 2 minutes.")

        # Determine last message details
        if last_msg.forward_from_chat:
            last_chat_id = last_msg.forward_from_chat.id
            last_msg_id = last_msg.forward_from_message_id
        elif last_msg.text and "/c/" in last_msg.text:
            try:
                last_chat_id = int("-100" + last_msg.text.split("/c/")[1].split("/")[0])
                last_msg_id = int(last_msg.text.split("/")[-1])
            except Exception:
                await message.reply_text("❌ Invalid last message link provided.")
                return
        else:
            await message.reply_text("❌ Please forward a valid message or send a proper message link.")
            return

        await ask2.delete()
        await last_msg.delete()

        # Validate same chat and order
        if chat_id != last_chat_id:
            await message.reply_text("❌ Both messages must be from the same channel.")
            return
        if last_msg_id < first_msg_id:
            await message.reply_text("❌ Last message ID must be greater than the first one.")
            return

        # Step 3: Fetch messages and save batch
        messages = []
        for msg_id in range(first_msg_id, last_msg_id + 1):
            try:
                msg = await client.get_messages(chat_id, msg_id)
                if msg:
                    messages.append({"chat_id": chat_id, "message_id": msg.id})
            except Exception as e:
                log.warning(f"Failed to fetch message {msg_id}: {e}")

        if not messages:
            await message.reply_text("❌ No valid messages found in that range.")
            return

        slug = generate_slug()
        if save_batch(slug, messages):
            await message.reply_text(
                f"✅ **Batch created successfully!**\n\n"
                f"🔗 Link: https://t.me/{client.me.username}?start={slug}"
            )
        else:
            await message.reply_text("⚠️ Failed to save batch. Please try again.")

    except Exception as e:
        log.exception("Unexpected error in /batch")
        await message.reply_text(f"⚠️ Unexpected error occurred: `{e}`")