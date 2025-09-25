import logging
from pyrogram import Client, filters
from pyromod import listen
from db_config import users_col

log = logging.getLogger("Settings")

# ---------------- HELP TEXTS ----------------
HELP_TEXT = {
    "BOT_TOKEN": "🔑 Your bot's token from BotFather.",
    "MONGO_URI": "🗄️ MongoDB connection URI string.",
    "AUTO_DELETE_TIME": "⏳ Time (in minutes) after which files auto-delete.",
    "VERIFY": "✅ Enable or disable verification system."
}

# ---------------- /settings COMMAND ----------------
@Client.on_message(filters.command("settings") & filters.private)
async def settings_handler(client, message):
    user_id = message.from_user.id
    user = users_col.find_one({"USER_ID": user_id}) or {}

    text = "⚙️ **Bot Settings**\n\n"
    text += "Choose a variable to edit or toggle."

    keyboard = [
        [
            ("Edit Bot Token", f"edit:BOT_TOKEN"),
            ("Edit Mongo URI", f"edit:MONGO_URI")
        ],
        [
            ("Edit Auto Delete Time", f"edit:AUTO_DELETE_TIME"),
            ("Toggle Verification", f"toggle:VERIFY")
        ],
        [("❌ Close", "close")]
    ]

    reply_markup = make_inline_keyboard(keyboard)
    await message.reply_text(text, reply_markup=reply_markup)

# ---------------- CALLBACK: EDIT ----------------
@Client.on_callback_query(filters.regex(r"^edit:(.+)"))
async def edit_variable(client, callback_query):
    user_id = callback_query.from_user.id
    var_name = callback_query.data.split(":")[1]

    await callback_query.message.reply_text(
        f"✏️ Send me the new value for **{var_name}**.\n\n{HELP_TEXT.get(var_name, '')}"
    )

    try:
        response = await client.listen(user_id, timeout=60)
    except Exception:
        return await callback_query.message.reply_text("⌛ Timed out. Try again.")

    new_value = response.text.strip()
    users_col.update_one(
        {"USER_ID": user_id},
        {"$set": {var_name: new_value}},
        upsert=True
    )

    log.info(f"{var_name} updated for {user_id}: {new_value}")
    await callback_query.message.reply_text(f"✅ **{var_name}** updated successfully.")

# ---------------- CALLBACK: TOGGLE ----------------
@Client.on_callback_query(filters.regex(r"^toggle:(.+)"))
async def toggle_variable(client, callback_query):
    user_id = callback_query.from_user.id
    var_name = callback_query.data.split(":")[1]

    user = users_col.find_one({"USER_ID": user_id}) or {}
    new_value = not bool(user.get(var_name, False))

    users_col.update_one(
        {"USER_ID": user_id},
        {"$set": {var_name: new_value}},
        upsert=True
    )

    log.info(f"{var_name} toggled for {user_id}: {new_value}")
    await callback_query.message.reply_text(
        f"🔄 **{var_name}** set to `{new_value}`"
    )

# ---------------- CALLBACK: CLOSE ----------------
@Client.on_callback_query(filters.regex(r"^close$"))
async def close_menu(client, callback_query):
    await callback_query.message.delete()

# ---------------- INLINE KEYBOARD HELPER ----------------
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def make_inline_keyboard(rows):
    return InlineKeyboardMarkup(
        [[InlineKeyboardButton(text, callback_data=data) for text, data in row] for row in rows]
    )