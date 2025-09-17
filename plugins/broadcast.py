from pyrogram import Client, filters
from pyrogram.errors import FloodWait, PeerIdInvalid, UserIsBlocked
import asyncio
import traceback
from collections import defaultdict
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

    success_users = []
    failure_reasons = defaultdict(int)

    status = await message.reply_text(f"📢 Starting broadcast to {total_users} users...")

    for user in users:
        user_id = user["_id"]
        try:
            await message.reply_to_message.copy(user_id)
            sent += 1
            success_users.append(str(user_id))
            await asyncio.sleep(0.05)  # avoid flood limits
        except FloodWait as e:
            await asyncio.sleep(e.value)
            try:
                await message.reply_to_message.copy(user_id)
                sent += 1
                success_users.append(str(user_id))
            except Exception as e_inner:
                failed += 1
                failure_reasons["Retry after FloodWait failed"] += 1
        except PeerIdInvalid:
            failed += 1
            failure_reasons["PeerIdInvalid"] += 1
        except UserIsBlocked:
            failed += 1
            failure_reasons["UserIsBlocked"] += 1
        except Exception:
            failed += 1
            failure_reasons["Other Errors"] += 1

    # Build detailed failure reason text
    failure_text = "\n".join([f"• {reason}: {count}" for reason, count in failure_reasons.items()]) or "None"

    result_text = (
        f"✅ Broadcast completed!\n\n"
        f"👥 Total Users: {total_users}\n"
        f"📨 Successfully Sent: {sent}\n"
        f"❌ Total Failed: {failed}\n\n"
        f"📋 Failure Breakdown:\n"
        f"{failure_text}"
    )

    await status.edit_text(result_text)