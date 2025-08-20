import re
from pyrogram import Client, filters
from pyrogram.errors import RPCError
from config import ADMINS
from database import save_batch


def serialize_entities(entities):
    """Convert Pyrogram MessageEntity objects into dicts for MongoDB storage"""
    if not entities:
        return []
    return [
        {
            "type": e.type,
            "offset": e.offset,
            "length": e.length,
            "url": e.url,
            "user": e.user.id if e.user else None,
            "language": e.language,
        }
        for e in entities
    ]


@Client.on_message(filters.command("batch") & filters.user(ADMINS))
async def create_batch(client, message):
    try:
        if len(message.command) < 3:
            await message.reply_text("⚠️ Usage:\n`/batch first_message_link last_message_link`", quote=True)
            return

        first_link = message.command[1]
        last_link = message.command[2]

        # Parse message links
        first_match = re.search(r"/(\d+)$", first_link)
        last_match = re.search(r"/(\d+)$", last_link)

        if not first_match or not last_match:
            await message.reply_text("❌ Invalid message links provided.", quote=True)
            return

        first_id = int(first_match.group(1))
        last_id = int(last_match.group(1))

        # Extract chat username or ID
        if "/c/" in first_link:
            chat_match = re.search(r"/c/(\d+)", first_link)
            if not chat_match:
                await message.reply_text("❌ Could not determine chat ID from first link.", quote=True)
                return
            chat_id = int("-100" + chat_match.group(1))
        else:
            chat_match = re.search(r"t.me/([^/]+)/", first_link)
            if not chat_match:
                await message.reply_text("❌ Could not determine chat username from first link.", quote=True)
                return
            chat_id = chat_match.group(1)

        # Collect messages
        batch_items = []
        for msg_id in range(first_id, last_id + 1):
            try:
                msg = await client.get_messages(chat_id, msg_id)
                if not msg:
                    continue

                item = {}

                # Store files
                if msg.document:
                    item["type"] = "document"
                    item["file_id"] = msg.document.file_id
                    item["caption"] = msg.caption or ""
                    item["caption_entities"] = serialize_entities(msg.caption_entities)
                elif msg.video:
                    item["type"] = "video"
                    item["file_id"] = msg.video.file_id
                    item["caption"] = msg.caption or ""
                    item["caption_entities"] = serialize_entities(msg.caption_entities)
                elif msg.photo:
                    item["type"] = "photo"
                    item["file_id"] = msg.photo.file_id
                    item["caption"] = msg.caption or ""
                    item["caption_entities"] = serialize_entities(msg.caption_entities)
                elif msg.text:
                    item["type"] = "text"
                    item["text"] = msg.text
                    item["entities"] = serialize_entities(msg.entities)
                else:
                    continue  # skip unsupported messages

                batch_items.append(item)

            except RPCError as e:
                await message.reply_text(f"⚠️ Failed to fetch message {msg_id}: {e}", quote=True)
                continue

        if not batch_items:
            await message.reply_text("❌