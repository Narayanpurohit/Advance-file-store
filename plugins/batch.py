import re
import secrets
import datetime
from pyrogram import Client, filters
from pyrogram.errors import FloodWait, ChannelInvalid, ChannelPrivate
from config import ADMINS
from database import save_batch


def generate_batch_slug():
    # 16-character random slug with "batch_" prefix
    return f"batch_{secrets.token_urlsafe(12)[:16]}"


@Client.on_message(filters.command("batch") & filters.user(ADMINS))
async def batch_handler(client, message):
    try:
        args = message.text.split()
        if len(args) != 3:
            await message.reply_text("❌ Usage: `/batch first_message_link last_message_link`", quote=True)
            return

        first_link = args[1]
        last_link = args[2]

        # Extract chat_id and message_id from t.me/c/... links
        match1 = re.search(r"t\.me/c/(-?\d+)/(\d+)", first_link)
        match2 = re.search(r"t\.me/c/(-?\d+)/(\d+)", last_link)

        if not match1 or not match2:
            await message.reply_text("❌ Invalid message links.", quote=True)
            return

        chat_id = int(f"-100{match1.group(1)}") if not match1.group(1).startswith("-100") else int(match1.group(1))
        first_msg_id = int(match1.group(2))
        last_msg_id = int(match2.group(2))

        if last_msg_id < first_msg_id:
            await message.reply_text("❌ Last message ID must be greater than first message ID.", quote=True)
            return

        messages = []
        async for msg in client.get_chat_history(chat_id, limit=last_msg_id - first_msg_id + 1, offset_id=first_msg_id - 1):
            if msg.id < first_msg_id or msg.id > last_msg_id:
                continue

            if msg.text:
                messages.append({
                    "type": "text",
                    "text": msg.text,
                    "entities": [entity.to_dict() for entity in (msg.entities or [])]
                })
            elif msg.document:
                messages.append({
                    "type": "document",
                    "file_id": msg.document.file_id,
                    "caption": msg.caption or "",
                    "caption_entities": [entity.to_dict() for entity in (msg.caption_entities or [])]
                })
            elif msg.video:
                messages.append({
                    "type": "video",
                    "file_id": msg.video.file_id,
                    "caption": msg.caption or "",
                    "caption_entities": [entity.to_dict() for entity in (msg.caption_entities or [])]
                })
            elif msg.photo:
                messages.append({
                    "type": "photo",
                    "file_id": msg.photo.file_id,
                    "caption": msg.caption or "",
                    "caption_entities": [entity.to_dict() for entity in (msg.caption_entities or [])]
                })

        if not messages:
            await message.reply_text("❌ No valid messages found in given range.", quote=True)
            return

        slug = generate_batch_slug()
        save_batch(slug, messages)

        await message.reply_text(
            f"✅ Batch created successfully!\n\n"
            f"🔑 Slug: `{slug}`\n"
            f"📌 Total messages saved: **{len(messages)}**",
            quote=True
        )

    except ChannelInvalid:
        await message.reply_text("❌ Invalid channel ID or bot is not in the channel.", quote=True)
    except ChannelPrivate:
        await message.reply_text("❌ Channel is private. Add the bot to the channel and try again.", quote=True)
    
    except FloodWait as e:
        await message.reply_text(f"⏳ Flood wait: retry after {e.value} seconds.", quote=True)
    except Exception as e:
        await message.reply_text(f"⚠️ Unexpected error: `{e}`", quote=True)