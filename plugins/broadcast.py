from pyrogram import Client, filters
from pyrogram.errors import FloodWait, PeerIdInvalid, UserIsBlocked
import asyncio
from collections import defaultdict
import traceback

#from bot import #ADMINS
from database import get_all_users, get_total_users
ADMINS=()
@Client.on_message(filters.command("broadcast") & filters.user(ADMINS))
async def broadcast_handler(client, message):
    if not message.reply_to_message:
        await message.reply_text("⚠️ Reply to a message to broadcast.")
        return

    users = get_all_users()
    total_users = len(users)
    sent = 0
    failed = 0
    failure_reasons = defaultdict(int)

    status = await message.reply_text(f"📢 Starting broadcast to {total_users} users...")

    for user_id in users:
        try:
            await message.reply_to_message.copy(user_id)
            sent += 1
            await asyncio.sleep(0.05)  # prevent flood
        except FloodWait as e:
            await asyncio.sleep(e.value)
            try:
                await message.reply_to_message.copy(user_id)
                sent += 1
            except Exception:
                failed += 1
                failure_reasons["Retry after FloodWait failed"] += 1
        except PeerIdInvalid:
            failed += 1
            failure_reasons["PeerIdInvalid"] += 1
        except UserIsBlocked:
            failed += 1
            failure_reasons["UserIsBlocked"] += 1
        except Exception as e:
            failed += 1
            failure_reasons[type(e).__name__] += 1  # count by error type
            # optional: log traceback to console
            traceback.print_exc()

    failure_text = "\n".join([f"• {reason}: {count}" for reason, count in failure_reasons.items()]) or "None"

    result_text = (
        f"✅ Broadcast completed!\n\n"
        f"👥 Total Users in DB: {get_total_users()}\n"
        f"📨 Successfully Sent: {sent}\n"
        f"❌ Failed: {failed}\n\n"
        f"📋 Failure Breakdown:\n{failure_text}"
    )

    await status.edit_text(result_text)