import re
import datetime
import secrets
from pyrogram import Client, filters
from pyrogram.types import Message
from database import batches_col

# Regex to parse message links (t.me/c/... for private channels)
LINK_REGEX = re.compile(r"(https?://t\.me/(c/)?(-?\d+)?/(\d+))")

def parse_link(link: str):
    """
    Parse a Telegram message link into (chat_id, message_id).
    Works for public and private channels.
    """
    match = LINK_REGEX.match(link)
    if not match:
        return None, None
    if match.group(2):  # private channel (t.me/c/<id>/<msg>)
        chat_id = int("-100" + match.group(3))
    else:
        chat_id = match.group(3)  # may be None for public username links
    message_id = int(match.group(4))
    return chat_id, message_id


@Client.on_message(filters.command("batch") & filters.private)
async def create_batch(client: Client, message: Message):
    try:
        args = message.text.split()
        if len(args) != 3:
            await message.reply_text("❌ Usage:\n`/batch <first_message_link> <last_message_link>`")
            return

        first_link, last_link = args[1], args[2]
        first_chat, first_id = parse_link(first_link)
        last_chat, last_id = parse_link(last_link)

        if not first_chat or not first_id or not last_id:
            await message.reply_text("❌ Invalid links provided.")
            return

        if first_chat != last_chat:
            await message.reply_text("⚠️ Both links must be from the same channel.")
            return

        # Try fetching to check access
        try:
            first_msg = await client.get_messages(first_chat, first_id)
        except Exception as e:
            await message.reply_text(f"❌ Cannot access channel or message: `{e}`")
            return

        # Loop through range of messages
        items = []
        for msg_id in range(first_id, last_id + 1):
            try:
                msg = await client.get_messages(first_chat, msg_id)
                if not msg:
                    continue

                if msg.text:
                    items.append({
                        "type": "text",
                        "text": msg.text,
                        "entities": [e.to_dict() for e in (msg.entities or [])]
                    })

                elif msg.document:
                    items.append({
                        "type": "document",
                        "file_id": msg.document.file_id,
                        "file_name": msg.document.file_name,
                        "caption": msg.caption or "",
                        "caption_entities": [e.to_dict() for e in (msg.caption_entities or [])]
                    })

                elif msg.video:
                    items.append({
                        "type": "video",
                        "file_id": msg.video.file_id,
                        "caption": msg.caption or "",
                        "caption_entities": [e.to_dict() for e in (msg.caption_entities or [])]
                    })

                elif msg.photo:
                    items.append({
                        "type": "photo",
                        "file_id": msg.photo.file_id,
                        "caption": msg.caption or "",
                        "caption_entities": [e.to_dict() for e in (msg.caption_entities or [])]
                    })

                # (add more types if needed: audio, voice, etc.)

            except Exception:
                continue

        if not items:
            await message.reply_text("❌ No valid messages found in given range.")
            return

        slug = "batch_" + secrets.token_urlsafe(6)
        batches_col.insert_one({
            "_id": slug,
            "created_at": datetime.datetime.utcnow(),
            "items": items
        })

        await message.reply_text(f"✅ Batch created successfully!\n\nSlug: `{slug}`")

    except Exception as e:
        await message.reply_text(f"❌ Error while creating batch: `{e}`")