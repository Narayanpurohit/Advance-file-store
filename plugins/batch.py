import random
import string
import datetime
from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.errors import FloodWait, ChannelInvalid, ChannelPrivate
from config import ADMINS
from database import save_batch


def generate_batch_slug() -> str:
    return "batch_" + "".join(random.choices(string.ascii_letters + string.digits, k=16))


@Client.on_message(filters.command("batch") & filters.user(ADMINS))
async def batch_handler(client: Client, message: Message):
    try:
        if len(message.command) != 3:
            await message.reply_text("⚠️ Usage:\n`/batch first_message_link last_message_link`")
            return

        first_link = message.command[1]
        last_link = message.command[2]

        # Extract channel ID and message IDs from links
        try:
            first_parts = first_link.split("/")
            last_parts = last_link.split("/")
            channel_id = int(first_parts[-2]) if first_parts[-2].startswith("-100") else None
            first_msg_id = int(first_parts[-1])
            last_msg_id = int(last_parts[-1])

            if not channel_id:
                await message.reply_text("❌ Invalid channel/message link format.")
                return
        except Exception:
            await message.reply_text("❌ Could not parse message links.")
            return

        # Fetch messages from channel
        try:
            msgs = await client.get_messages(channel_id, range(first_msg_id, last_msg_id + 1))
        except ChannelInvalid:
            await message.reply_text("❌ Invalid channel. Make sure bot is added.")
            return
        except ChannelPrivate:
            await message.reply_text("❌ Bot is not a member of this channel or it’s private.")
            return
        except FloodWait as e:
            await message.reply_text(f"⏳ FloodWait: retry after {e.value} seconds.")
            return
        except Exception as e:
            await message.reply_text(f"⚠️ Unexpected error while fetching messages:\n`{e}`")
            return

        # Collect valid messages
        collected = []
        for m in msgs:
            if not m:
                continue
            if m.text:
                collected.append({
                    "type": "text",
                    "text": m.text,
                    "entities": [ent.__dict__ for ent in (m.entities or [])]
                })
            elif m.document:
                collected.append({
                    "type": "document",
                    "file_id": m.document.file_id,
                    "caption": m.caption or "",
                    "caption_entities": [ent.__dict__ for ent in (m.caption_entities or [])]
                })
            elif m.photo:
                collected.append({
                    "type": "photo",
                    "file_id": m.photo.file_id,
                    "caption": m.caption or "",
                    "caption_entities": [ent.__dict__ for ent in (m.caption_entities or [])]
                })

        if not collected:
            await message.reply_text("❌ No valid messages found in given range.")
            return

        # Generate random slug
        slug = generate_batch_slug()

        # Save to DB
        await save_batch(slug, collected)

        await message.reply_text(
            f"✅ Batch created successfully!\n\nSlug: `{slug}`"
        )

    except Exception as e:
        await message.reply_text(f"⚠️ Unexpected error: {e}")