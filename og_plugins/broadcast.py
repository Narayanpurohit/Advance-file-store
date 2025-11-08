from pyrogram import Client, filters
from pyrogram.errors import FloodWait, PeerIdInvalid, UserIsBlocked, ChatWriteForbidden
import asyncio
from collections import defaultdict
import traceback
from db_config import users_col  # Your DB user collection
from config import CODE2_ADMINS as ADMINS  # Should contain list of admin user IDs


@Client.on_message(filters.command("broadcast") & filters.private)
async def broadcast_handler(client, message):
    # Admin check
    if message.from_user.id not in ADMINS:
        return await message.reply_text("❌ You are not authorized to use this command.")

    # Require reply to a message
    if not message.reply_to_message:
        return await message.reply_text("⚠️ Reply to a message to broadcast.")

    users = users_col.find()  # Fetch all users from DB
    total_users = users_col.count_documents({})
    sent = 0
    failed = 0
    reasons = defaultdict(int)

    status = await message.reply_text(f"📢 **Broadcast Started**\n\nSending to `{total_users}` users...")

    for user in users:
        user_id = user.get("user_id") or user.get("_id")  # adjust based on your DB structure
        if not user_id:
            continue

        try:
            await message.reply_to_message.copy(user_id)
            sent += 1
            await asyncio.sleep(0.05)

        except FloodWait as e:
            await asyncio.sleep(e.value)
            try:
                await message.reply_to_message.copy(user_id)
                sent += 1
            except Exception:
                failed += 1
                reasons["Retry after FloodWait failed"] += 1

        except PeerIdInvalid:
            failed += 1
            reasons["PeerIdInvalid"] += 1

        except UserIsBlocked:
            failed += 1
            reasons["UserIsBlocked"] += 1

        except ChatWriteForbidden:
            failed += 1
            reasons["ChatWriteForbidden"] += 1

        except Exception as e:
            failed += 1
            reasons[type(e).__name__] += 1
            traceback.print_exc()

    breakdown = "\n".join([f"• {error}: {count}" for error, count in reasons.items()]) or "No errors ✅"

    final_text = (
        "✅ **Broadcast Completed!**\n\n"
        f"👥 **Total Users:** `{total_users}`\n"
        f"📨 **Sent:** `{sent}`\n"
        f"❌ **Failed:** `{failed}`\n\n"
        f"📋 **Failure Breakdown:**\n{breakdown}"
    )

    await status.edit_text(final_text)