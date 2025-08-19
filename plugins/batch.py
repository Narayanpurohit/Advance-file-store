import re
import logging
from pyrogram import Client, filters
from database import add_batch

log = logging.getLogger(__name__)

LINK_REGEX = re.compile(r"https://t\.me/(c/)?([a-zA-Z0-9_]+)/(\d+)")

def parse_link(link: str):
    """Extract chat_id (or username) and message_id from a t.me link."""
    m = LINK_REGEX.match(link)
    if not m:
        return None, None
    is_private = bool(m.group(1))
    chat_part = m.group(2)
    msg_id = int(m.group(3))
    if is_private:
        chat_id = int("-100" + chat_part)  # private channels use -100 prefix
    else:
        chat_id = chat_part
    return chat_id, msg_id


@Client.on_message(filters.command("batch") & filters.user([123456789]))  # replace with your admin IDs
async def batch_handler(client, message):
    args = message.text.split()
    if len(args) != 3:
        await message.reply_text("❌ Usage: `/batch <first_msg_link> <last_msg_link>`", quote=True)
        return

    first_link, last_link = args[1], args[2]
    first_chat, first_id = parse_link(first_link)
    last_chat, last_id = parse_link(last_link)

    if not first_chat or not first_id or not last_chat or not last_id:
        await message.reply_text("❌ Invalid message links provided.", quote=True)
        return

    if first_chat != last_chat:
        await message.reply_text("❌ Start and end messages must be from the same channel.", quote=True)
        return

    if first_id > last_id:
        await message.reply_text("⚠️ Start message ID must be lower than end message ID.", quote=True)
        return

    try:
        # test fetching first/last messages
        test_first = await client.get_messages(first_chat, first_id)
        test_last = await client.get_messages(first_chat, last_id)
        if not test_first or not test_last:
            await message.reply_text("❌ Could not fetch start or end messages. Make sure the bot is in the channel.", quote=True)
            return
    except Exception as e:
        log.error(f"Error fetching messages: {e}")
        await message.reply_text(f"❌ Could not fetch messages: {e}", quote=True)
        return

    items = []
    for msg_id in range(first_id, last_id + 1):
        try:
            msg = await client.get_messages(first_chat, msg_id)
            if not msg:
                continue

            if msg.text or msg.caption:
                items.append({
                    "type": "text" if msg.text else "file",
                    "text": msg.text.html if msg.text else None,
                    "file_id": None,
                    "caption": msg.caption.html if msg.caption else None
                })

            if msg.document:
                items.append({
                    "type": "doc",
                    "file_id": msg.document.file_id,
                    "caption": msg.caption.html if msg.caption else ""
                })
            elif msg.video:
                items.append({
                    "type": "vid",
                    "file_id": msg.video.file_id,
                    "caption": msg.caption.html if msg.caption else ""
                })
            elif msg.audio:
                items.append({
                    "type": "aud",
                    "file_id": msg.audio.file_id,
                    "caption": msg.caption.html if msg.caption else ""
                })

        except Exception as e:
            log.warning(f"Skipping message {msg_id} due to error: {e}")
            continue

    if not items:
        await message.reply_text("❌ No valid messages found in given range.", quote=True)
        return

    slug = add_batch(first_chat, first_id, last_id, items)
    await message.reply_text(f"✅ Batch created!\n\nHere’s your link:\n`/start batch_{slug}`", quote=True)