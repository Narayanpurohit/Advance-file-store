import re
import random
import string
from typing import Optional, Tuple, Union, List, Dict

from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.errors import (
    ChannelInvalid,
    ChannelPrivate,
    ChatAdminRequired,
    FloodWait,
    RPCError,
)

from config import ADMINS
from database import save_batch
from datetime import datetime

# ====== Config-like locals (safe defaults if not in config.py) ======
MAX_BATCH_MESSAGES = 300  # hard cap to avoid huge ranges
# ====================================================================


def _generate_slug(length: int = 16) -> str:
    """Return a random slug like 'batch_aZ9...'"
    """
    return "batch_" + "".join(random.choices(string.ascii_letters + string.digits, k=length))


def _clean_entities(entities) -> List[Dict]:
    """Convert Pyrogram MessageEntity objects to plain JSON-safe dicts."""
    if not entities:
        return []
    cleaned = []
    for e in entities:
        cleaned.append({
            "type": str(e.type),        # e.g. 'MessageEntityType.BOLD'
            "offset": e.offset,
            "length": e.length,
            "url": getattr(e, "url", None),
            "user_id": getattr(e, "user", None).id if getattr(e, "user", None) else None,
            "language": getattr(e, "language", None),
            "custom_emoji_id": getattr(e, "custom_emoji_id", None),
        })
    return cleaned


def _parse_link(arg: str) -> Optional[Tuple[Union[int, str], int]]:
    """
    Accepts:
      - https://t.me/c/<internal_id>/<msg_id>   (private channel)
      - https://t.me/<username>/<msg_id>        (public channel)
    Returns: (chat_ref, msg_id) where chat_ref is int -100XXXX or str username.
    """
    # private: /c/123456789/100
    m = re.match(r"https?://t\.me/c/(\d+)/(\d+)$", arg)
    if m:
        internal_id = int(m.group(1))
        msg_id = int(m.group(2))
        chat_ref = int(f"-100{internal_id}")
        return chat_ref, msg_id

    # public: /username/100
    m2 = re.match(r"https?://t\.me/([A-Za-z0-9_]+)/(\d+)$", arg)
    if m2:
        username = m2.group(1)
        msg_id = int(m2.group(2))
        return username, msg_id

    return None


async def _fetch_message_safe(client: Client, chat_ref: Union[int, str], msg_id: int) -> Optional[Message]:
    """Get a single message with friendly error mapping."""
    try:
        return await client.get_messages(chat_id=chat_ref, message_ids=msg_id)
    except ChannelInvalid:
        raise RuntimeError("❌ Invalid channel. Double-check the links.")
    except ChannelPrivate:
        raise RuntimeError("❌ Bot has no access to this channel. Add the bot as **Admin**.")
    except ChatAdminRequired:
        raise RuntimeError("❌ Bot needs **Admin** rights to read messages in this channel.")
    except FloodWait as e:
        raise RuntimeError(f"⏳ FloodWait: please retry in {e.value} seconds.")
    except RPCError as e:
        raise RuntimeError(f"⚠️ Telegram RPC error: {e}")
    except Exception as e:
        raise RuntimeError(f"⚠️ Unexpected fetch error: {e}")


def _serialize_message(msg: Message) -> Optional[Dict]:
    """
    Turn a Pyrogram Message into a JSON-safe dict we can store.
    We keep only what's needed to reproduce it later (type, file_id, text/caption, entities).
    """
    if msg.document:
        return {
            "type": "document",
            "file_id": msg.document.file_id,
            "caption": msg.caption or "",
            "caption_entities": _clean_entities(msg.caption_entities),
        }
    if msg.video:
        return {
            "type": "video",
            "file_id": msg.video.file_id,
            "caption": msg.caption or "",
            "caption_entities": _clean_entities(msg.caption_entities),
        }
    if msg.audio:
        return {
            "type": "audio",
            "file_id": msg.audio.file_id,
            "caption": msg.caption or "",
            "caption_entities": _clean_entities(msg.caption_entities),
        }
    if msg.photo:
        # Pyrogram's .photo is the biggest size Photo; use its file_id
        return {
            "type": "photo",
            "file_id": msg.photo.file_id,
            "caption": msg.caption or "",
            "caption_entities": _clean_entities(msg.caption_entities),
        }
    if msg.text:
        return {
            "type": "text",
            "text": msg.text,
            "entities": _clean_entities(msg.entities),
        }
    # Ignore other message types (stickers, polls, etc.)
    return None


@Client.on_message(filters.command("batch") & filters.user(ADMINS))
async def batch_handler(client: Client, message: Message):
    """
    Usage:
      /batch <first_msg_link> <last_msg_link>
    Examples:
      /batch https://t.me/c/123456789/10 https://t.me/c/123456789/25
      /batch https://t.me/MyPublicChannel/10 https://t.me/MyPublicChannel/25
    """
    try:
        if len(message.command) != 3:
            return await message.reply_text(
                "❌ Usage:\n"
                "`/batch <first_msg_link> <last_msg_link>`\n\n"
                "Examples:\n"
                "`/batch https://t.me/c/123456789/10 https://t.me/c/123456789/25`\n"
                "`/batch https://t.me/MyChannel/10 https://t.me/MyChannel/25`",
                quote=True
            )

        first_link = message.command[1].strip()
        last_link = message.command[2].strip()

        parsed_first = _parse_link(first_link)
        parsed_last = _parse_link(last_link)
        if not parsed_first or not parsed_last:
            return await message.reply_text("❌ Invalid link(s). Please send proper Telegram message links.", quote=True)

        chat_ref_1, first_id = parsed_first
        chat_ref_2, last_id = parsed_last

        if chat_ref_1 != chat_ref_2:
            return await message.reply_text("❌ Both links must be from the **same** channel.", quote=True)

        chat_ref = chat_ref_1

        if last_id < first_id:
            first_id, last_id = last_id, first_id

        total = (last_id - first_id + 1)
        if total > MAX_BATCH_MESSAGES:
            return await message.reply_text(
                f"❌ Range is too large ({total} messages). "
                f"Max allowed is {MAX_BATCH_MESSAGES}.",
                quote=True
            )

        # Try fetching a single message to validate access early
        test_msg = await _fetch_message_safe(client, chat_ref, first_id)
        if not test_msg:
            return await message.reply_text("❌ Couldn't fetch the first message. Check access and IDs.", quote=True)

        collected: List[Dict] = []
        skipped = 0

        for mid in range(first_id, last_id + 1):
            try:
                msg = await _fetch_message_safe(client, chat_ref, mid)
            except RuntimeError as e:
                return await message.reply_text(str(e), quote=True)

            if not msg:
                skipped += 1
                continue

            ser = _serialize_message(msg)
            if ser:
                collected.append(ser)
            else:
                skipped += 1  # unsupported type

        if not collected:
            return await message.reply_text("❌ No valid messages found in given range.", quote=True)

        slug = _generate_slug()

        # Save synchronously (our database.py uses PyMongo sync calls)
        try:
            save_batch(slug, collected)
        except Exception as e:
            return await message.reply_text(f"⚠️ Failed to save batch: {e}", quote=True)

        # Build shareable link
        bot_username = (await client.get_me()).username or "YourBot"
        link = f"https://t.me/{bot_username}?start={slug}"

        extra = f"\n\nℹ️ Skipped: {skipped}" if skipped else ""
        await message.reply_text(
            f"✅ Batch created successfully!\n\n"
            f"🔗 Link: {link}"
            f"{extra}",
            quote=True
        )

    except Exception as e:
        # Final catch-all so admins always get feedback
        await message.reply_text(f"⚠️ Unexpected error: {e}", quote=True)