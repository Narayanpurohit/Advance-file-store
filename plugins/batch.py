import re
import random
import string
from pyrogram import Client, filters
from pyrogram.errors import FloodWait, ChannelInvalid, ChannelPrivate
from config import ADMINS
from database import save_batch


def generate_slug(length: int = 16) -> str:
    """Generate a random slug of given length."""
    return "batch_" + ''.join(random.choices(string.ascii_letters + string.digits, k=length))


@Client.on_message(filters.command("batch") & filters.user(ADMINS))
async def create_batch(_, message):
    try:
        # Expecting two links: first_message_link last_message_link
        if len(message.command) != 3:
            await message.reply_text("❌ Usage: `/batch first_message_link last_message_link`", quote=True)
            return

        first_link = message.command[1]
        last_link = message.command[2]

        # Extract channel ID and message IDs from links
        try:
            def extract_ids(link: str):
                parts = link.split("/")
                if "t.me/c/" in link:
                    # /c/ style link -> need to prepend -100
                    chat_id = int("-100" + parts[-2])
                else:
                    # username style (t.me/username/1234)
                    chat_id = parts[-2] if parts[-2].startswith("-100") else parts[-2]
                msg_id = int(parts[-1])
                return int(chat_id), msg_id

            channel_id, first_msg_id = extract_ids(first_link)
            _, last_msg_id = extract_ids(last_link)

        except Exception:
            await message.reply_text("❌ Invalid channel/message link format.", quote=True)
            return

        if first_msg_id > last_msg_id:
            await message.reply_text("❌ First message ID must be smaller than last message ID.", quote=True)
            return

        saved_messages = []

        for msg_id in range(first_msg_id, last_msg_id + 1):
            try:
                msg = await _.get_messages(channel_id, msg_id)
                if not msg:
                    continue

                # Text message
                if msg.text:
                    saved_messages.append({
                        "type": "text",
                        "text": msg.text,
                        "entities": [e.to_json() for e in msg.entities] if msg.entities else None
                    })

                # Documents, Videos, Photos
                elif msg.document:
                    saved_messages.append({
                        "type": "document",
                        "file_id": msg.document.file_id,
                        "caption": msg.caption,
                        "caption_entities": [e.to_json() for e in msg.caption_entities] if msg.caption_entities else None
                    })
                elif msg.video:
                    saved_messages.append({
                        "type": "video",
                        "file_id": msg.video.file_id,
                        "caption": msg.caption,
                        "caption_entities": [e.to_json() for e in msg.caption_entities] if msg.caption_entities else None
                    })
                elif msg.photo:
                    saved_messages.append({
                        "type": "photo",
                        "file_id": msg.photo.file_id,
                        "caption": msg.caption,
                        "caption_entities": [e.to_json() for e in msg.caption_entities] if msg.caption_entities else None
                    })

            except FloodWait as e:
                await asyncio.sleep(e.value)
            except Exception:
                continue

        if not saved_messages:
            await message.reply_text("❌ No valid messages found in given range.", quote=True)
            return

        slug = generate_slug()
        await save_batch(slug, saved_messages)

        await message.reply_text(
            f"✅ Batch created successfully!\n\nSlug: `{slug}`",
            quote=True
        )

    except ChannelInvalid:
        await message.reply_text("❌ Invalid channel ID or link.", quote=True)
    except ChannelPrivate:
        await message.reply_text("❌ Bot is not a member of the channel or channel is private.", quote=True)
    except Exception as e:
        await message.reply_text(f"⚠️ Unexpected error: {e}", quote=True)