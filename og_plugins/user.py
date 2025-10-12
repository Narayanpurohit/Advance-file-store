from pyrogram import Client, filters
from db_config import users_col
from config import CODE2_ADMINS


@Client.on_message(filters.command("deleteuser") & filters.user(CODE2_ADMINS))
async def delete_user_handler(client, message):
    try:
        args = message.text.split()

        # ✅ Check command format
        if len(args) != 2:
            return await message.reply_text("Usage: /deleteuser <user_id>")

        user_id = int(args[1])

        # ✅ Find user
        user = users_col.find_one({"USER_ID": user_id})
        if not user:
            return await message.reply_text("❌ User not found in database.")

        db_name = user.get("DB_NAME", "N/A")

        # ✅ Delete user
        result = users_col.delete_one({"USER_ID": user_id})
        if result.deleted_count > 0:
            await message.reply_text(
                f"🗑️ User `{user_id}` has been deleted successfully.\n"
                f"💾 Database name: `{db_name}`"
            )
        else:
            await message.reply_text("⚠️ Deletion failed. Try again later.")

    except Exception as e:
        await message.reply_text(f"⚠️ Error while deleting user: {e}")