from pyrogram import Client, filters
from delete_user import delete_user  # import the function we created
import logging

log = logging.getLogger(__name__)

# 🛡️ Replace with your admin IDs
from config import CODE2_ADMINS as ADMINS  # <--- change this to your Telegram user IDs


@Client.on_message(filters.command("delete") & filters.private)
async def delete_user_command(client, message):
    user_id = message.from_user.id

    # Check admin access
    if user_id not in ADMINS:
        await message.reply_text("⛔ You are not authorized to use this command.")
        return

    # Parse the command
    parts = message.text.strip().split()
    if len(parts) != 2:
        await message.reply_text("⚠️ Usage: `/delete <user_id>`", quote=True)
        return

    try:
        target_id = int(parts[1])
    except ValueError:
        await message.reply_text("❌ Invalid user ID. It must be a number.", quote=True)
        return

    # Try to delete user
    result = delete_user(target_id)
    if result:
        await message.reply_text(f"✅ User `{target_id}` has been deleted from the database.", quote=True)
        log.info(f"🗑️ Admin {user_id} deleted user {target_id}")
    else:
        await message.reply_text(f"⚠️ No user found with ID `{target_id}`.", quote=True)
        log.warning(f"⚠️ Admin {user_id} tried to delete non-existing user {target_id}")