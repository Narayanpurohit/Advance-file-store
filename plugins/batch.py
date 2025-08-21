import random
import string
from datetime import datetime
from pyrogram import Client, filters
from pyrogram.types import Message
from config import ADMINS
from database import save_batch

def generate_slug(length=16):
    """Generate a random slug with fixed length"""
    return "batch_" + "".join(random.choices(string.ascii_letters + string.digits, k=length - 6))

def serialize_entities(entities):
    """Convert MessageEntity objects into plain dicts"""
    if not entities:
        return []
    result = []
    for e in entities:
        result.append({
            "type": str(e.type),   # enum -> string
            "offset": e.offset,
            "length": e.length,
            "url": e.url,
            "user_id": getattr(e.user, "id", None) if e.user else None,
            "language": e.language,
            "custom_emoji_id": e.custom_emoji_id
        })
    return result

def serialize_message(msg: Message):
    """Convert Pyrogram Message into plain dict"""
    if msg.document:
        return {
            "type": "document",
            "file_id": msg.document.file_id,
            "caption": msg.caption,
            "caption_entities": serialize_entities(msg.caption_entities)
        }
    elif msg.video:
        return {
            "type": "video",
            "file_id": msg.video.file_id,
            "caption": msg.caption,
            "caption_entities": serialize_entities(msg.caption_entities)
        }
    elif msg.text:
        return {
            "type": "text",
            "text": msg.text,
            "entities": serialize_entities(msg.entities)
        }
    else:
        return None

@Client.on_message(filters.command("batch") & filters.user(ADMINS))
async def batch_handler(client, message: Message):
    try:
        if len(message.command) < 4:
            return await message.reply("❌ Usage: /batch channel_id first_msg_id last_msg_id")

        channel_id = int(message.command[1])
        first_id = int(message.command[2])
        last_id = int(message.command[3])

        collected = []
        for msg_id in range(first_id, last_id + 1):
            try:
                msg = await client.get_messages(channel_id, msg_id)
                if not msg:
                    continue
                data = serialize_message(msg)
                if data:
                    collected.append(data)
            except Exception as e:
                print(f"DEBUG: error fetching message {msg_id}: {e}")

        if not collected:
            return await message.reply("❌ No valid messages found in given range.")

        slug = generate_slug()
        await save_batch(slug, collected)

        await message.reply(
            f"✅ Batch created successfully!\n\n"
            f"Slug: `{slug}`"
        )

    except Exception as e:
        await message.reply(f"⚠️ Unexpected error: {e}")