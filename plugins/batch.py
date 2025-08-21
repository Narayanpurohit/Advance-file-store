import random
import string
import re
from datetime import datetime
from pyrogram import Client, filters
from pyrogram.types import Message

from config import ADMINS
from database import save_batch


# Function to generate random slug
def generate_slug(length=16):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))


# Parse arguments (channel_id/message_id or Telegram link)
def parse_arg(arg: str):
    match = re.match(r"https?://t\.me/c/(\d+)/(\d+)", arg)
    if match:
        channel_id = int(f"-100{match.group(1)}")
        msg_id = int(match.group(2))
        return channel_id, msg_id
    # fallback to number
    try:
        return None, int(arg)
    except:
        return None, None


@Client.on_message(filters.command("batch") & filters.user(ADMINS))
async def batch_handler(client: Client, message: Message):
    args = message.text.split()
    
    if len(args) != 3:
        return await message.reply(
            "❌ Usage:\n"
            "`/batch <channel_id> <first_id> <last_id>`\n"
            "Or:\n"
            "`/batch <link1> <link2>`"
        )

    # Parse args
    ch1, first_id = parse_arg(args[1])
    ch2, last_id = parse_arg(args[2])
    channel_id = ch1 or ch2

    if not channel_id or not first_id or not last_id:
        return await message.reply("❌ Could not determine channel_id or message range.")

    if first_id > last_id:
        first_id, last_id = last_id, first_id

    messages_data = []

    for msg_id in range(first_id, last_id + 1):
        try:
            msg = await client.get_messages(chat_id=channel_id, message_ids=msg_id)

            if not msg:
                continue

            if msg.document:
                messages_data.append({
                    "type": "document",
                    "file_id": msg.document.file_id,
                    "caption": msg.caption or "",
                    "caption_entities": [ce.__dict__ for ce in (msg.caption_entities or [])]
                })
            elif msg.video:
                messages_data.append({
                    "type": "video",
                    "file_id": msg.video.file_id,
                    "caption": msg.caption or "",
                    "caption_entities": [ce.__dict__ for ce in (msg.caption_entities or [])]
                })
            elif msg.photo:
                messages_data.append({
                    "type": "photo",
                    "file_id": msg.photo.file_id,
                    "caption": msg.caption or "",
                    "caption_entities": [ce.__dict__ for ce in (msg.caption_entities or [])]
                })
            elif msg.text:
                messages_data.append({
                    "type": "text",
                    "text": msg.text,
                    "entities": [e.__dict__ for e in (msg.entities or [])]
                })

        except Exception as e:
            print(f"⚠️ Error fetching message {msg_id}: {e}")
            continue

    if not messages_data:
        return await message.reply("❌ No valid messages found in given range.")

    slug = "batch_" + generate_slug(16)

    try:
        await save_batch(slug, messages_data)
        await message.reply(f"✅ Batch created successfully!\n\nSlug: `{slug}`")
    except Exception as e:
        await message.reply(f"⚠️ Unexpected error: {e}")