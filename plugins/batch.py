import datetime
from pyrogram import Client, filters
from pyrogram.errors import RPCError, ChannelInvalid, ChannelPrivate
from config import ADMINS
from database import save_batch

# --- Helper: serialize entities ---
def serialize_entities(entities):
    """Convert Pyrogram MessageEntity objects into dicts for MongoDB storage"""
    if not entities:
        return []
    serialized = []
    for e in entities:
        serialized.append({
            "type": str(e.type),   # ✅ Convert Enum to string
            "offset": e.offset,
            "length": e.length,
            "url": e.url,
            "user": e.user.id if e.user else None,
            "language": e.language,
        })
    return serialized


@Client.on_message(filters.command("batch") & filters.user(ADMINS))
async def batch_handler(client, message):
    try:
        if len(message.command) != 3:
            await message.reply_text("❌ Usage:\n`/batch first_message_link last_message_link`")
            return

        first_link = message.command[1]
        last_link = message.command[2]

        try:
            # Extract chat_id and message_id from t.me/c/ or t.me/ links
            def extract_ids(link):
                if "/c/" in link:
                    parts = link.split("/")
                    chat_id = int("-100" + parts[-2])  # private supergroup/channel
                    msg_id = int(parts[-1])
                    return chat_id, msg_id
                else:
                    raise ValueError("Unsupported link format")

            chat_id, first_id = extract_ids(first_link)
            _, last_id = extract_ids(last_link)

        except Exception:
            await message.reply_text("❌ Invalid link format. Make sure to use full `t.me/c/...` links.")
            return

        if first_id > last_id:
            first_id, last_id = last_id, first_id

        messages = []
        for msg_id in range(first_id, last_id + 1):
            try:
                msg = await client.get_messages(chat_id, msg_id)
                if not msg:
                    continue

                # Text messages
                if msg.text:
                    messages.append({
                        "type": "text",
                        "text": msg.text,
                        "entities": serialize_entities(msg.entities),
                    })

                # Files (documents, videos, audios, photos)
                elif msg.document:
                    messages.append({
                        "type": "document",
                        "file_id": msg.document.file_id,
                        "caption": msg.caption,
                        "caption_entities": serialize_entities(msg.caption_entities),
                    })
                elif msg.video:
                    messages.append({
                        "type": "video",
                        "file_id": msg.video.file_id,
                        "caption": msg.caption,
                        "caption_entities": serialize_entities(msg.caption_entities),
                    })
                elif msg.audio:
                    messages.append({
                        "type": "audio",
                        "file_id": msg.audio.file_id,
                        "caption": msg.caption,
                        "caption_entities": serialize_entities(msg.caption_entities),
                    })
                elif msg.photo:
                    messages.append({
                        "type": "photo",
                        "file_id": msg.photo.file_id,
                        "caption": msg.caption,
                        "caption_entities": serialize_entities(msg.caption_entities),
                    })

            except RPCError:
                continue

        if not messages:
            await message.reply_text("❌ No valid messages found in the given range.")
            return

        # Generate batch slug
        slug = f"batch_{chat_id}_{first_id}_{last_id}"

        # Save to DB
        save_batch(slug, messages)

        await message.reply_text(f"✅ Batch created successfully!\n\nSlug: `{slug}`")

    except ChannelInvalid:
        await message.reply_text("❌ Bot is not in the channel or channel is invalid.")
    except ChannelPrivate:
        await message.reply_text("❌ Bot cannot access this channel (it's private).")
    except Exception as e:
        await message.reply_text(f"⚠️ Unexpected error: {e}")