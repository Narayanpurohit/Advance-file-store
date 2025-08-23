import logging
import random
import string
from pyrogram import Client, filters
from database import save_batch

log = logging.getLogger(__name__)


def generate_slug(length: int = 16) -> str:
    """Generate a unique random slug."""
    return "batch_" + ''.join(random.choices(string.ascii_letters + string.digits, k=length))


@Client.on_message(filters.command("batch") & filters.private)
async def batch_handler(client, message):
    try:
        args = message.text.split()

        if len(args) != 3:
            await message.reply_text("❌ Usage:\n`/batch <first_msg_link> <last_msg_link>`")
            return

        first_url = args[1]
        last_url = args[2]

        # Extract message IDs
        try:
            chat_id = int("-100" + first_url.split("/c/")[1].split("/")[0])
            first_msg_id = int(first_url.split("/")[-1])
            last_msg_id = int(last_url.split("/")[-1])
        except Exception:
            await message.reply_text("❌ Invalid message links provided.")
            return

        if last_msg_id < first_msg_id:
            await message.reply_text("❌ Last message ID must be greater than first.")
            return

        messages = []
        for msg_id in range(first_msg_id, last_msg_id + 1):
            try:
                msg = await client.get_messages(chat_id, msg_id)
                if msg:
                    messages.append({"chat_id": chat_id, "message_id": msg.id})
            except Exception as e:
                log.warning(f"Failed to fetch message {msg_id}: {e}")

        if not messages:
            await message.reply_text("❌ No valid messages found in given range.")
            return

        slug = generate_slug()
        if save_batch(slug, messages):
            await message.reply_text(
                f"✅ Batch created successfully!\n\n"
                f"🔗 Link: https://t.me/{client.me.username}?start={slug}"
            )
        else:
            await message.reply_text("⚠️ Failed to save batch. Please try again.")

    except Exception as e:
        log.exception("Unexpected error in /batch")
        await message.reply_text(f"⚠️ Unexpected error: {e}")