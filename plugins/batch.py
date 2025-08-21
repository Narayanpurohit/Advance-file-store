import random
import string
from pyrogram import Client, filters
from pyrogram.errors import ChannelInvalid, ChannelPrivate, ChatAdminRequired
from config import ADMINS
from database import save_batch
import datetime


def generate_slug(length=16):
    return "batch_" + "".join(random.choices(string.ascii_letters + string.digits, k=length))


def clean_entities(entities):
    if not entities:
        return []
    cleaned = []
    for e in entities:
        cleaned.append({
            "type": str(e.type),
            "offset": e.offset,
            "length": e.length,
            "url": getattr(e, "url", None),
            "user": getattr(e, "user", None).id if getattr(e, "user", None) else None,
            "language": getattr(e, "language", None),
            "custom_emoji_id": getattr(e, "custom_emoji_id", None)
        })
    return cleaned


@Client.on_message(filters.command("batch") & filters.user(ADMINS))
async def batch_handler(client, message):
    try:
        if len(message.command) != 3:
            return await message.reply_text("❌ Usage:\n`/batch first_msg_link last_msg_link`")

        first_link = message.command[1]
        last_link = message.command[2]

        # Extract channel ID and message IDs
        try:
            first_parts = first_link.split("/")
            last_parts = last_link.split("/")
            channel_id = int("-100" + first_parts[-2])  # from /c/<id>/<msg_id>
            first_msg_id = int(first_parts[-1])
            last_msg_id = int(last_parts[-1])
        except Exception:
            return await message.reply_text("❌ Invalid links format. Please send Telegram private channel links like:\n`/batch https://t.me/c/123456789/10 https://t.me/c/123456789/20`")

        if last_msg_id < first_msg_id:
            return await message.reply_text("❌ Last message ID must be greater than first message ID.")

        messages = []

        for msg_id in range(first_msg_id, last_msg_id + 1):
            try:
                msg = await client.get_messages(chat_id=channel_id, message_ids=msg_id)
            except ChannelInvalid:
                return await message.reply_text("❌ Invalid channel ID.")
            except ChannelPrivate:
                return await message.reply_text("❌ Bot has no access to this channel (make sure bot is admin).")
            except ChatAdminRequired:
                return await message.reply_text("❌ Bot requires admin rights to access channel messages.")
            except Exception as e:
                return await message.reply_text(f"⚠️ Failed to fetch message {msg_id}: {e}")

            if not msg:
                continue

            if msg.document:
                messages.append({
                    "type": "document",
                    "file_id": msg.document.file_id,
                    "caption": msg.caption or "",
                    "caption_entities": clean_entities(msg.caption_entities)
                })
            elif msg.video:
                messages.append({
                    "type": "video",
                    "file_id": msg.video.file_id,
                    "caption": msg.caption or "",
                    "caption_entities": clean_entities(msg.caption_entities)
                })
            elif msg.text:
                messages.append({
                    "type": "text",
                    "text": msg.text,
                    "entities": clean_entities(msg.entities)
                })

        if not messages:
            return await message.reply_text("❌ No valid messages found in given range.")

        slug = generate_slug()
        await save_batch(slug, messages)

        await message.reply_text(f"✅ Batch created successfully!\n\nSlug: `{slug}`")

    except Exception as e:
        await message.reply_text(f"⚠️ Unexpected error: {e}")