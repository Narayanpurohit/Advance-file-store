import logging
import asyncio
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from db_config import users_col
from pyrogram.enums import ParseMode

# ---------------- LOGGING ----------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - [%(levelname)s] - %(name)s - %(message)s"
)
log = logging.getLogger("Settings")

# ---------------- VARIABLES ----------------
BOOLEAN_VARS = ["ENABLE_FSUB", "VERIFICATION_MODE", "AUTO_DELETE"]
INT_VARS = ["PREMIUM_HOURS_VERIFICATION", "AUTO_DELETE_TIME"]

VARIABLE_INFO = {
    "BOT_TOKEN": {
        "name": "🤖 Bot Token",
        "help": "The token you get from @BotFather to run your bot."
    },
    "MONGO_URI": {
        "name": "🗄️ MongoDB URI",
        "help": 'Connection string for your MongoDB database.\n\nClick here for <a href="https://youtu.be/4d-07F-Z2dc?si=_8OIuEJoL5oT1kQr">tutorial link</a>.'
    },
    "ADMINS": {
        "name": "👮 Admin Users",
        "help": "User IDs of admins who can control the bot.\nExample: 123456789,987654321"
    },
    "FSUB": {
        "name": "🔗 Force Subscribe Channel",
        "help": "Username or channel ID users must join before using the bot.\nExample: @MyChannel or -1001234567890"
    },
    "PREMIUM_HOURS_VERIFICATION": {
        "name": "💎 Premium Verification Hours",
        "help": "Number of hours a verified user stays verified.\nExample: 12"
    },
    "SHORTENER_DOMAIN": {
        "name": "🌐 Shortener Domain",
        "help": "The domain used for your link shortener.\nExample: short.example.com"
    },
    "SHORTENER_API_KEY": {
        "name": "🔑 Shortener API Key",
        "help": "API key for your shortener service."
    },
    "CAPTION": {
        "name": "📝 File Caption",
        "help": "Default caption text for files sent by the bot."
    },
    "LOG_CHANNEL_ID": {
        "name": "📢 Log Channel",
        "help": "Telegram channel ID where logs will be sent.\nExample: -1001234567890"
    },
    "AUTO_DELETE_TIME": {
        "name": "⏰ Auto Delete Time",
        "help": "Time (in seconds) after which files are auto-deleted.\nExample: 1800"
    },
    "ENABLE_FSUB": {
        "name": "✅ Enable Force Subscribe",
        "help": "Set to True to enable force-subscribe feature."
    },
    "VERIFICATION_MODE": {
        "name": "🛡️ Verification Mode",
        "help": "Set to True to enable verification system."
    },
    "AUTO_DELETE": {
        "name": "🗑️ Auto Delete",
        "help": "Set to True to enable auto-deleting of files after set time."
    }
}

# ---------------- GROUPS ----------------
GROUPS = {
    "Required Settings": ["BOT_TOKEN", "MONGO_URI", "LOG_CHANNEL_ID"],
    "Admins": ["ADMINS"],
    "Force Sub": ["ENABLE_FSUB", "FSUB"],
    "Verification": ["VERIFICATION_MODE", "PREMIUM_HOURS_VERIFICATION", "SHORTENER_DOMAIN", "SHORTENER_API_KEY"],
    "Auto Delete": ["AUTO_DELETE", "AUTO_DELETE_TIME"],
    "Caption": ["CAPTION"]
}


# ---------------- KEYBOARDS ----------------
def get_group_keyboard():
    buttons = []
    for group in GROUPS.keys():
        buttons.append([InlineKeyboardButton(group, callback_data=f"group:{group}")])
    buttons.append([InlineKeyboardButton("❌ Close", callback_data="close")])
    return InlineKeyboardMarkup(buttons)


def get_variable_keyboard(group_name: str):
    buttons = []
    for var in GROUPS[group_name]:
        label = VARIABLE_INFO.get(var, {}).get("name", var)
        buttons.append([InlineKeyboardButton(label, callback_data=f"setting:{group_name}:{var}")])
    buttons.append([
        InlineKeyboardButton("⬅️ Back", callback_data="back_to_groups"),
        InlineKeyboardButton("❌ Close", callback_data="close")
    ])
    return InlineKeyboardMarkup(buttons)


def get_setting_keyboard(group_name: str, var_name: str, is_boolean=False):
    buttons = []
    if is_boolean:
        buttons.append([InlineKeyboardButton("🔄 Toggle", callback_data=f"toggle:{group_name}:{var_name}")])
    else:
        buttons.append([InlineKeyboardButton("✏️ Edit", callback_data=f"edit:{group_name}:{var_name}")])
    buttons.append([
        InlineKeyboardButton("⬅️ Back", callback_data=f"back_to_group:{group_name}"),
        InlineKeyboardButton("❌ Close", callback_data="close")
    ])
    return InlineKeyboardMarkup(buttons)


def get_edit_keyboard(group_name: str, var_name: str):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("⬅️ Back", callback_data=f"back_to_setting:{group_name}:{var_name}")]
    ])


# ---------------- HANDLERS ----------------
@Client.on_message(filters.command("settings") & filters.private)
async def settings_handler(client, message):
    user_id = message.from_user.id
    log.info(f"User {user_id} opened settings.")
    text = "⚙️ <b>Bot Settings</b>\n\nChoose a category to configure:"
    await message.reply_text(text, reply_markup=get_group_keyboard(), parse_mode=ParseMode.HTML)


@Client.on_callback_query(filters.regex(r"^group:(.+)"))
async def open_group(client, callback_query):
    group_name = callback_query.data.split(":", 1)[1]
    text = f"📂 <b>{group_name}</b>\n\nChoose a variable to configure:"
    await callback_query.message.edit_text(
        text,
        reply_markup=get_variable_keyboard(group_name),
        parse_mode=ParseMode.HTML
    )


@Client.on_callback_query(filters.regex(r"^setting:(.+?):(.+)"))
async def open_setting(client, callback_query):
    group_name, var_name = callback_query.data.split(":", 2)[1:]
    user = users_col.find_one({"USER_ID": callback_query.from_user.id}) or {}
    current_value = user.get(var_name, "Not set")

    var_info = VARIABLE_INFO.get(var_name, {"name": var_name, "help": ""})
    text = (
        f"<b>{var_info['name']}</b>\n\n"
        f"<b>Current Value:</b>\n<code>{current_value}</code>\n\n"
        f"{var_info['help']}"
    )

    keyboard = get_setting_keyboard(group_name, var_name, var_name in BOOLEAN_VARS)
    await callback_query.message.edit_text(text, reply_markup=keyboard, parse_mode=ParseMode.HTML, disable_web_page_preview=True)


@Client.on_callback_query(filters.regex(r"^toggle:(.+?):(.+)"))
async def toggle_setting(client, callback_query):
    group_name, var_name = callback_query.data.split(":", 2)[1:]
    user_id = callback_query.from_user.id
    user = users_col.find_one({"USER_ID": user_id}) or {}
    current_value = bool(user.get(var_name, False))
    new_value = not current_value
    users_col.update_one({"USER_ID": user_id}, {"$set": {var_name: new_value}})
    log.info(f"Toggled {var_name} for {user_id}: {current_value} → {new_value}")
    await open_setting(client, callback_query)


@Client.on_callback_query(filters.regex(r"^edit:(.+?):(.+)"))
async def edit_setting(client, callback_query):
    group_name, var_name = callback_query.data.split(":", 2)[1:]
    var_info = VARIABLE_INFO.get(var_name, {"name": var_name, "help": ""})

    await callback_query.message.edit_text(
        f"✏️ Send a new value for <b>{var_info['name']}</b>.\n\n"
        f"{var_info['help']}\n\n"
        "⏳ You have 120 seconds.",
        reply_markup=get_edit_keyboard(group_name, var_name),
        parse_mode=ParseMode.HTML,
        disable_web_page_preview=True
    )

    while True:
        try:
            response = await client.listen(callback_query.message.chat.id, timeout=120)
        except asyncio.TimeoutError:
            await open_setting(client, callback_query)
            return

        if response.text and response.text.startswith("/"):
            continue

        new_value = response.text.strip()

        # int validation
        if var_name in INT_VARS:
            if not new_value.isdigit():
                await callback_query.message.reply_text("❌ Please send a valid integer.")
                continue
            new_value = int(new_value)

        users_col.update_one({"USER_ID": callback_query.from_user.id}, {"$set": {var_name: new_value}})
        log.info(f"Updated {var_name} for {callback_query.from_user.id}: {new_value}")
        await callback_query.message.reply_text(f"✅ {var_info['name']} updated successfully.")
        await open_setting(client, callback_query)
        return


# ---------------- BACK & CLOSE ----------------
@Client.on_callback_query(filters.regex(r"^back_to_groups$"))
async def back_to_groups(client, callback_query):
    await callback_query.message.edit_text(
        "⚙️ <b>Bot Settings</b>\n\nChoose a category to configure:",
        reply_markup=get_group_keyboard(),
        parse_mode=ParseMode.HTML
    )


@Client.on_callback_query(filters.regex(r"^back_to_group:(.+)"))
async def back_to_group(client, callback_query):
    group_name = callback_query.data.split(":", 1)[1]
    await open_group(client, callback_query)


@Client.on_callback_query(filters.regex(r"^back_to_setting:(.+?):(.+)"))
async def back_to_setting(client, callback_query):
    await open_setting(client, callback_query)


@Client.on_callback_query(filters.regex(r"^close$"))
async def close_menu(client, callback_query):
    await callback_query.message.delete()