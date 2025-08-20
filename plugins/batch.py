import re
import random
import string
from pyrogram import Client, filters
from pyrogram.errors import FloodWait, ChannelInvalid, ChannelPrivate
from config import ADMINS
from database import save_batch

# Regex for t.me/c/ links
LINK_REGEX = re.compile(r"https?://t\.me/c/(-?\d+)/(\d+)")

def random_slug(length=16):
    """Generate a random slug of given length."""
    return "batch_" + ''.join(random.choices(string.ascii_letters + string.digits, k=length))

@Client.on_message(filters.command("batch") & filters.user(ADMINS))
async def batch_handler(client, message):
    try:
        if len(message.command) < 3:
            await message.reply_text("❌ Usage:\n`/batch first_message_link last_message_link`")
            return

        first_link = message.command[1]
        last_link = message.command[2]

        # Parse links
        first_match = LINK_REGEX.match(first_link)
        last_match = LINK_REGEX.match(last_link)

        if not first_match or not last_match:
            await message.reply_text("❌ Invalid channel/message link format.")
            return

        channel_id_1, first_msg_id = first_match.groups()
        channel_id_2, last_msg_id = last_match.groups()

        if channel_id_1 != channel_id_2:
            await message.reply_text("❌ Both links must belong to the same channel.")
            return

        channel_id = int(f"-100{channel_id_1}") if not channel_id_1.startswith("-100") else int(channel_id_1)
        first_msg_id = int(first_msg_id)
        last_msg_id = int(last_msg_id)

        if first_msg_id > last_msg_id:
            first_msg_id, last_msg_id = last_msg_id, first_msg_id

        batch_messages = []

        # Fetch messages one by one
        for i in range(first_msg_id, last_msg_id + 1):
            try:
                msg = await client.get_messages(channel_id, i)
                print(f"DEBUG: fetched message {i}: {msg}")  # Debug log

                if not msg:
                    continue

                if msg.text:
                    batch_messages.append({
                        "type": "text",
                        "text": msg.text,
                        "entities": [e.to_dict() for e in msg.entities] if msg.entities else []
                    })
                elif msg.document:
                    batch_messages.append({
                        "type": "document",
                        "file_id": msg.document.file_id,
                        "caption": msg.caption or "",
                        "caption_entities": [e.to_dict() for e in msg.caption_entities] if msg.caption_entities else []
                    })
                elif msg.video:
                    batch_messages.append({
                        "type": "video",
                        "file_id": msg.video.file_id,
                        "caption": msg.caption or "",
                        "caption_entities": [e.to_dict() for e in msg.caption_entities] if msg.caption_entities else []
                    })
                elif msg.photo:
                    batch_messages.append({
                        "type": "photo",
                        "file_id": msg.photo.file_id,
                        "caption": msg.caption or "",
                        "caption_entities": [e.to_dict() for e in msg.caption_entities] if msg.caption_entities else []
                    })
                else:
                    print(f"DEBUG: message {i} skipped (unsupported type).")

            except FloodWait as e:
                print(f"DEBUG: FloodWait for {e.value} seconds at message {i}")
                await asyncio.sleep(e.value)
                continue
            except Exception as e:
                print(f"DEBUG: error fetching message {i}: {e}")
                continue

        if not batch_messages:
            await message.reply_text("❌ No valid messages found in given range.")
            return

        # Generate random slug
        slug = random_slug()

        # Save to DB
        await save_batch(slug, batch_messages)

        await message.reply_text(
            f"✅ Batch created successfully!\n\n"
            f"Slug: `{slug}`\n"
            f"Total messages saved: {len(batch_messages)}"
        )

    except ChannelInvalid:
        await message.reply_text("❌ Invalid channel. Please check the channel ID or link.")
    except ChannelPrivate:
        await message.reply_text("❌ Bot has no access to this channel. Add it as admin and try again.")
    except Exception as e:
        await message.reply_text(f"⚠️ Unexpected error: {e}")