# plugins/broadcast.py

from pyrogram import Client, filters
from pyrogram.errors import FloodWait, PeerIdInvalid, UserIsBlocked
import asyncio
from database import get_all_users
from bot import ADMINS

@Client.on_message(filters.command("broadcast") & filters.user(ADMINS))
async def broadcast_handler(client, message):
    if not message.reply_to_message:
        await message.reply_text("⚠️ Reply to a message to broadcast.")
        return

    users = get_all_users()
    total_users = len(users)
    sent = 0
    failed = 0

    status = await message.reply_text(f"📢 Starting broadcast to {total_users} users...")

    for user in users:
        try:
            await message.reply_to_message.copy(user["_id"])
            sent += 1
            await asyncio.sleep(0.05)  # avoid hitting flood limits
        except FloodWait as e:
            await asyncio.sleep(e.value)
            try:
                await message.reply_to_message.copy(user["_id"])
                sent += 1
            except:
                failed += 1
        except (PeerIdInvalid, UserIsBlocked):
            failed += 1
        except Exception:
            failed += 1

    await status.edit_text(
        f"✅ Broadcast completed!\n\n👥 Total: {total_users}\n📨 Sent: {sent}\n❌ Failed: {failed}"
    )