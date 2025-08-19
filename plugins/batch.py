import re
import logging
import asyncio
from pyrogram import Client, filters
from pyrogram.errors import ChatAdminRequired, ChannelPrivate, PeerIdInvalid, FloodWait
from database import save_batch
from config import ADMINS  # ✅ use ADMINS from config

log = logging.getLogger(__name__)

# Extract chat_id and message_id from a t.me/c/ link
def parse_message_link(link: str):
    try:
        match = re.search(r"t\.me/c/(\d+)/(\d+)", link)
        if not match:
            return None, None
        chat_id = int("-100" + match.group(1))  # convert to full chat_id
        message_id = int(match.group(2))
        return chat_id, message_id
    except Exception as e:
        log.error(f"Failed to parse link {link}: {e}")
        return None, None


@Client.on_message(filters.command("batch") & filters.user(ADMINS))  # ✅ admin filter
async def create_batch(client, message):
    try:
        args = message.text.split()
        if len(args) != 3:
            await message.reply_text("❌ Usage: `/batch first_message_link last_message_link`", quote=True)
            return

        first_link, last_link = args[1], args[2]
        first_chat, first_id = parse_message_link(first_link)
        last_chat, last_id = parse_message_link(last_link)

        if not first_chat or not last_chat or first_chat != last_chat:
            await message.reply_text("❌ Invalid or mismatched message links.", quote=True)
            return

        batch_items = []
        for msg_id in range(first_id, last_id + 1):
            try:
                msg = await client.get_messages(first_chat, msg_id)
                if not msg:
                    continue

                if msg.text or msg.caption:
                    content = msg.text or msg.caption
                    entities = msg.entities or msg.caption_entities
                    batch_items.append({
                        "type": "text" if msg.text else "file",
                        "content": content,
                        "entities": [e.__dict__ for e in entities] if entities else None,
                        "file_id": msg.document.file_id if msg.document else
                                   msg.video.file_id if msg.video else
                                   msg.audio.file_id if msg.audio else None,
                        "file_type": "doc" if msg.document else
                                     "vid" if msg.video else
                                     "aud" if msg.audio else None,
                        "file_name": msg.document.file_name if msg.document else None,
                        "file_size": msg.document.file_size if msg.document else
                                     msg.video.file_size if msg.video else
                                     msg.audio.file_size if msg.audio else None,
                    })

            except FloodWait as e:
                await message.reply_text(f"⏳ FloodWait: Sleeping for {e.value} seconds...", quote=True)
                await asyncio.sleep(e.value)
            except Exception as e:
                log.warning(f"Failed to fetch message {msg_id}: {e}")
                continue

        if not batch_items:
            await message.reply_text("❌ No valid messages found in given range.", quote=True)
            return

        slug = save_batch(batch_items)
        await message.reply_text(f"✅ Batch saved!\n\nHere’s your link:\n`/start {slug}`", quote=True)

    except (ChatAdminRequired, ChannelPrivate, PeerIdInvalid):
        await message.reply_text("❌ I can’t access the channel. Please add me as an admin.", quote=True)
    except Exception as e:
        log.error(f"Batch creation error: {e}", exc_info=True)
        await message.reply_text(f"⚠️ Unexpected error: {e}", quote=True)