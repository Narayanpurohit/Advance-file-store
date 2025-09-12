import logging
import asyncio
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from db_config import users_col
from config import VARIABLE_HELP_TEXTS
from pyrogram.enums import ParseMode

# ---------------- LOGGING ----------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - [%(levelname)s] - %(name)s - %(message)s"
)
log = logging.getLogger("Settings")

# ---------------- VARIABLES ----------------
BOOLEAN_VARS = ["ENABLE_FSUB", "VERIFICATION_MODE"]
NORMAL_VARS = [
    "BOT_TOKEN", "MONGO_URI",
    "ADMINS", "FSUB", "PREMIUM_HOURS_VERIFICATION", "VERIFY_SLUG_TTL_HOURS",
    "SHORTENER_DOMAIN", "SHORTENER_API_KEY", "CAPTION", "PREMIUM_POINTS", "LOG_CHANNEL_ID"
]

REQUIRED_VARS = [
    "BOT_TOKEN", "MONGO_URI", "LOG_CHANNEL_ID"
]

OPTIONAL_VARS = list(set(NORMAL_VARS) - set(REQUIRED_VARS))

# ---------------- MAIN MENU ----------------
def get_main_keyboard():
    buttons = [
        [InlineKeyboardButton("📝 Required Settings", callback_data="show_required")],
        [InlineKeyboardButton("⚙️ Optional Settings", callback_data="show_optional")]
    ]
    return InlineKeyboardMarkup(buttons)

def get_settings_keyboard(user_data: dict, variables: list):
    buttons = []
    for var in variables:
        val = user_data.get(var, "Not set")
        buttons.append(
            [InlineKeyboardButton(f"{var}: {val}", callback_data=f"setting:{var}")]
        )
    return InlineKeyboardMarkup(buttons)

@Client.on_message(filters.command("settings") & filters.private)
async def settings_handler(client, message):
    user_id = message.from_user.id
    try:
        log.info(f"User {user_id} accessed /settings.")
        text = "⚙️ Your Settings\n\nSelect a category to view and edit settings:"
        await message.reply_text(text, reply_markup=get_main_keyboard())

    except Exception as e:
        log.exception(f"Error in /settings for user {user_id}: {e}")
        await message.reply_text(f"⚠️ Something went wrong: {str(e)}")

# ---------------- CALLBACK HANDLER ----------------
@Client.on_callback_query(filters.regex(r"^show_(required|optional)$"))
async def show_settings_category(client, callback_query):
    user_id = callback_query.from_user.id
    category = callback_query.data.split("_")[1]

    try:
        user = users_col.find_one({"USER_ID": user_id}) or {}

        if category == "required":
            text = "📝 Required Settings"
            variables = REQUIRED_VARS
        else:
            text = "⚙️ Optional Settings"
            variables = OPTIONAL_VARS + BOOLEAN_VARS

        keyboard = get_settings_keyboard(user, variables)
        keyboard.inline_keyboard.append([InlineKeyboardButton("⬅️ Back", callback_data="back_to_main")])

        await callback_query.message.edit_text(text, reply_markup=keyboard)

    except Exception as e:
        log.exception(f"Error showing {category} settings for user {user_id}: {e}")
        await callback_query.answer(f"⚠️ Error: {str(e)}", show_alert=True)

@Client.on_callback_query(filters.regex(r"^setting:(.+)"))
async def setting_selected(client, callback_query):
    user_id = callback_query.from_user.id
    var_name = callback_query.data.split(":")[1]

    try:
        user = users_col.find_one({"USER_ID": user_id}) or {}
        current_value = user.get(var_name, "Not set")
        log.info(f"User {user_id} selected {var_name} (current: {current_value})")

        if var_name in BOOLEAN_VARS:
            text = f"{var_name}: {current_value}"
            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("Toggle", callback_data=f"toggle:{var_name}")],
                [InlineKeyboardButton("⬅️ Back", callback_data="back_to_main")]
            ])
        else:
            text = f"{var_name}\nCurrent Value:\n{current_value}"
            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("Edit", callback_data=f"edit:{var_name}")],
                [InlineKeyboardButton("⬅️ Back", callback_data="back_to_main")]
            ])

        await callback_query.message.edit_text(text, reply_markup=keyboard)

    except Exception as e:
        log.exception(f"Error handling setting:{var_name} for user {user_id}: {e}")
        await callback_query.answer(f"⚠️ Error: {str(e)}", show_alert=True)

@Client.on_callback_query(filters.regex(r"^toggle:(.+)"))
async def toggle_boolean(client, callback_query):
    user_id = callback_query.from_user.id
    var_name = callback_query.data.split(":")[1]

    try:
        user = users_col.find_one({"USER_ID": user_id}) or {}
        current_value = bool(user.get(var_name, False))
        new_value = not current_value

        users_col.update_one({"USER_ID": user_id}, {"$set": {var_name: new_value}})
        log.info(f"Toggled {var_name}: {current_value} → {new_value} (user {user_id})")

        await callback_query.message.edit_text(
            f"{var_name} updated: {new_value}",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("⬅️ Back", callback_data="back_to_main")]
            ])
        )

    except Exception as e:
        log.exception(f"Error toggling {var_name} for user {user_id}: {e}")
        await callback_query.answer(f"⚠️ Error: {str(e)}", show_alert=True)

@Client.on_callback_query(filters.regex(r"^edit:(.+)"))
async def edit_variable(client, callback_query):
    user_id = callback_query.from_user.id
    var_name = callback_query.data.split(":")[1]
    var_help_text = VARIABLE_HELP_TEXTS.get(var_name, "")

    try:
        await callback_query.message.edit_text(
    f"Send new value for *{var_name}*.\n\n{var_help_text}\n\n"
    "You have 120 seconds. Send /cancel to abort.",
    parse_mode=ParseMode.HTML
)

        try:
            response = await client.listen(callback_query.message.chat.id, timeout=120)

        except asyncio.TimeoutError:
            log.warning(f"Timeout waiting for input on {var_name} (user {user_id})")
            await callback_query.message.reply_text("⏰ Timeout! Back to main settings.")
            await settings_handler(client, callback_query.message)
            return

        if response.text.lower() == "/cancel":
            log.info(f"User {user_id} cancelled editing {var_name}")
            await callback_query.message.reply_text("Cancelled. Back to main settings.")
            await settings_handler(client, callback_query.message)
            return

        new_value = response.text
        users_col.update_one({"USER_ID": user_id}, {"$set": {var_name: new_value}})
        log.info(f"{var_name} updated for user {user_id}: {new_value}")

        await callback_query.message.reply_text(f"{var_name} updated to:\n{new_value}")
        await settings_handler(client, callback_query.message)

    except Exception as e:
        log.exception(f"Error editing {var_name} for user {user_id}: {e}")
        await callback_query.message.reply_text(f"Error updating setting: {str(e)}")

@Client.on_callback_query(filters.regex(r"^back_to_main$"))
async def back_to_main_settings(client, callback_query):
    user_id = callback_query.from_user.id
    try:
        text = "Your Settings\nSelect a category to view and edit settings:"
        await callback_query.message.edit_text(text, reply_markup=get_main_keyboard())

    except Exception as e:
        log.exception(f"Error returning to main settings menu for user {user_id}: {e}")
        await callback_query.answer(f"Error: {str(e)}", show_alert=True)