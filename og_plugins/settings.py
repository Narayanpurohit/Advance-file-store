import logging
import asyncio
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pymongo import MongoClient
from config import MONGO_URI2, DB_NAME

# ---------------- LOGGING ----------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - [%(levelname)s] - %(name)s - %(message)s"
)
log = logging.getLogger("Settings")

# ---------------- MONGO ----------------
mongo_client = MongoClient(MONGO_URI2)
db = mongo_client[DB_NAME]
users_col = db["users"]

# ---------------- VARIABLES ----------------
BOOLEAN_VARS = ["ENABLE_FSUB", "VERIFICATION_MODE"]
NORMAL_VARS = [
    "BOT_TOKEN", "API_ID", "API_HASH", "MONGO_URI", "DB_NAME",
    "ADMINS", "FSUB", "PREMIUM_HOURS_VERIFICATION", "VERIFY_SLUG_TTL_HOURS",
    "SHORTENER_DOMAIN", "SHORTENER_API_KEY", "CAPTION", "PREMIUM_POINTS"
]


# ---------------- MAIN MENU ----------------
def get_settings_keyboard(user_data: dict):
    buttons = []
    for var in BOOLEAN_VARS + NORMAL_VARS:
        val = user_data.get(var, None)
        buttons.append(
            [InlineKeyboardButton(f"{var}: {val}", callback_data=f"setting:{var}")]
        )
    return InlineKeyboardMarkup(buttons)


@Client.on_message(filters.command("settings") & filters.private)
async def settings_handler(client, message):
    user_id = message.from_user.id
    try:
        user = users_col.find_one({"USER_ID": user_id})
        if not user:
            log.warning(f"Unauthorized user {user_id} tried to access settings.")
            await message.reply_text("❌ You are not registered in the database.")
            return

        log.info(f"User {user_id} accessed /settings.")
        text = "⚙️ **Your Settings**\n\nSelect a variable to edit:"
        await message.reply_text(text, reply_markup=get_settings_keyboard(user))

    except Exception as e:
        log.exception(f"Error in /settings for user {user_id}: {e}")
        await message.reply_text("⚠️ Something went wrong while opening settings.")


# ---------------- CALLBACK HANDLER ----------------
@Client.on_callback_query(filters.regex(r"^setting:(.+)"))
async def setting_selected(client, callback_query):
    user_id = callback_query.from_user.id
    var_name = callback_query.data.split(":")[1]

    try:
        user = users_col.find_one({"USER_ID": user_id})
        if not user:
            log.error(f"User {user_id} not found in DB when selecting {var_name}")
            await callback_query.answer("Not found in DB", show_alert=True)
            return

        current_value = user.get(var_name, None)
        log.info(f"User {user_id} selected {var_name} (current: {current_value})")

        if var_name in BOOLEAN_VARS:
            text = f"⚡ {var_name}: `{current_value}`"
            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("🔄 Toggle", callback_data=f"toggle:{var_name}")],
                [InlineKeyboardButton("⬅️ Back", callback_data="back_to_settings")]
            ])
        else:
            text = f"✏️ **{var_name}**\nCurrent Value:\n`{current_value}`"
            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("Edit", callback_data=f"edit:{var_name}")],
                [InlineKeyboardButton("⬅️ Back", callback_data="back_to_settings")]
            ])

        await callback_query.message.edit_text(text, reply_markup=keyboard)

    except Exception as e:
        log.exception(f"Error handling setting:{var_name} for user {user_id}: {e}")
        await callback_query.answer("⚠️ Error loading setting", show_alert=True)


# ---------------- TOGGLE BOOLEAN ----------------
@Client.on_callback_query(filters.regex(r"^toggle:(.+)"))
async def toggle_boolean(client, callback_query):
    user_id = callback_query.from_user.id
    var_name = callback_query.data.split(":")[1]

    try:
        user = users_col.find_one({"USER_ID": user_id})
        if not user:
            log.error(f"Toggle failed - User {user_id} not found in DB.")
            await callback_query.answer("Not found in DB", show_alert=True)
            return

        current_value = bool(user.get(var_name, False))
        new_value = not current_value

        users_col.update_one({"USER_ID": user_id}, {"$set": {var_name: new_value}})
        log.info(f"✅ {var_name} toggled from {current_value} → {new_value} (user {user_id})")

        await callback_query.message.edit_text(
            f"⚡ {var_name} updated: `{new_value}`",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("⬅️ Back", callback_data="back_to_settings")]
            ])
        )

    except Exception as e:
        log.exception(f"Error toggling {var_name} for user {user_id}: {e}")
        await callback_query.answer("⚠️ Toggle failed", show_alert=True)


# ---------------- EDIT NORMAL VAR ----------------
@Client.on_callback_query(filters.regex(r"^edit:(.+)"))
async def edit_variable(client, callback_query):
    user_id = callback_query.from_user.id
    var_name = callback_query.data.split(":")[1]

    try:
        await callback_query.message.edit_text(
            f"✏️ Send me the new value for **{var_name}**.\n\n"
            f"You have 120 seconds. Send /cancel to abort."
        )

        try:
            response = await client.listen(callback_query.message.chat.id, filters=filters.text, timeout=120)
        except asyncio.TimeoutError:
            log.warning(f"Timeout waiting for input on {var_name} (user {user_id})")
            await callback_query.message.reply_text("⏰ Timeout! Back to settings.")
            await settings_handler(client, callback_query.message)
            return

        if response.text.lower() == "/cancel":
            log.info(f"User {user_id} cancelled editing {var_name}")
            await callback_query.message.reply_text("❌ Cancelled. Back to settings.")
            await settings_handler(client, callback_query.message)
            return

        new_value = response.text
        users_col.update_one({"USER_ID": user_id}, {"$set": {var_name: new_value}})
        log.info(f"✅ {var_name} updated for user {user_id}: {new_value}")

        await callback_query.message.reply_text(f"✅ {var_name} updated to:\n`{new_value}`")
        await settings_handler(client, callback_query.message)

    except Exception as e:
        log.exception(f"Error editing {var_name} for user {user_id}: {e}")
        await callback_query.message.reply_text("⚠️ Failed to update setting.")


# ---------------- BACK TO SETTINGS ----------------
@Client.on_callback_query(filters.regex(r"^back_to_settings$"))
async def back_to_settings(client, callback_query):
    user_id = callback_query.from_user.id
    try:
        user = users_col.find_one({"USER_ID": user_id})
        if not user:
            log.error(f"Back to settings failed - User {user_id} not in DB.")
            await callback_query.answer("Not found in DB", show_alert=True)
            return

        log.info(f"User {user_id} returned to settings menu.")
        await callback_query.message.edit_text(
            "⚙️ **Your Settings**\n\nSelect a variable to edit:",
            reply_markup=get_settings_keyboard(user)
        )

    except Exception as e:
        log.exception(f"Error returning to settings menu for user {user_id}: {e}")
        await callback_query.answer("⚠️ Failed to go back", show_alert=True)