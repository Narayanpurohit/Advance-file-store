import logging
import asyncio
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.enums import ParseMode
from db_config import users_col


# ---------------- LOGGING ----------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - [%(levelname)s] - %(name)s - %(message)s"
)
log = logging.getLogger("Settings")


# ---------------- VARIABLES ----------------
BOOLEAN_VARS = ["ENABLE_FSUB", "VERIFICATION_MODE", "AUTO_DELETE",
                "PROTECT_CONTENT", "CLONE_BUTTON", "PUBLIC_BOT","DEKOY"]

INT_VARS = ["PREMIUM_HOURS_VERIFICATION", "AUTO_DELETE_TIME",
            "LOG_CHANNEL"]


VARIABLE_INFO = {
    "BOT_TOKEN": {"name": "ʙᴏᴛ ᴛᴏᴋᴇɴ", "help": "ᴛʜᴇ ᴛᴏᴋᴇɴ ʏᴏᴜ ɢᴇᴛ ғʀᴏᴍ @ʙᴏᴛғᴀᴛʜᴇʀ."},
    "DB_NAME": {"name": "Data code", "help": "ᴛʜɪs ɪs ᴜɴɪǫᴜᴇ ᴄᴏᴅᴇ ᴛʜᴀᴛ sᴛᴏʀᴇs ʏᴏᴜʀ ʟɪɴᴋs ᴀɴᴅ ᴜsᴇʀ ᴅᴀᴛᴀ ɪꜰ ʏᴏᴜ ᴄʜᴀɴɢᴇ ᴀᴄᴏᴜɴᴛ sᴇᴛ ᴛʜɪs ᴄᴏᴅᴇ."},
    "ADMINS": {"name": "ᴀᴅᴍɪɴ ᴜsᴇʀs", "help": "ᴜsᴇʀ ɪᴅs ᴏғ ᴀᴅᴍɪɴs sᴇᴘᴀʀᴀᴛᴇ ᴛʜᴇᴍ ᴡɪᴛʜ ,"},
    "FSUB": {"name": "ғᴏʀᴄᴇ sᴜʙ ᴄʜᴀɴɴᴇʟ", "help": "ɪᴅ ᴏғ ᴄʜᴀɴɴᴇʟ ғᴏʀ ғsᴜʙ ɪɴ ᴛʜɪs ғᴏʀᴍᴀᴛ. \n\nʙᴜᴛᴛᴏɴ ɴᴀᴍᴇ 1 : ɪᴅ1 , ʙᴜᴛᴛᴏɴ ɴᴀᴍᴇ 2 : ɪᴅ2 , ʙᴜᴛᴛᴏɴ ɴᴀᴍᴇ 3 : ɪᴅ3"},
    "PREMIUM_HOURS_VERIFICATION": {"name": "ʜᴏᴜʀs ᴜsᴇʀ ɢᴇᴛ ᴘʀᴇᴍɪᴜᴍ ᴀғᴛᴇʀ ᴠᴇʀɪғɪᴇᴅ.", "help": "ʜᴏᴜʀs ᴜsᴇʀ sᴛᴀʏs ᴠᴇʀɪғɪᴇᴅ."},
    "SHORTENER_DOMAIN": {"name": "sʜᴏʀᴛᴇɴᴇʀ ᴅᴏᴍᴀɪɴ", "help": "ᴏɴʟʏ ᴅᴏᴍᴀɪɴ ғᴏʀ ʟɪɴᴋ sʜᴏʀᴛᴇɴᴇʀ. ʟɪᴋᴇ ᴛʜɪs ᴅᴏᴍᴀɪɴ.ᴄᴏᴍ"},
    "SHORTENER_API_KEY": {"name": "sʜᴏʀᴛᴇɴᴇʀ ᴀᴘɪ ᴋᴇʏ", "help": "ᴀᴘɪ ᴋᴇʏ ғᴏʀ ʏᴏᴜʀ sʜᴏʀᴛᴇɴᴇʀ."},
    "CAPTION": {"name": "ғɪʟᴇ ᴄᴀᴘᴛɪᴏɴ", "help": "ʏᴏᴜ ᴄᴀɴ ᴜsᴇ ᴛʜɪs ғᴏʀᴍᴀᴛs ᴀs ᴄᴀᴘᴛɪᴏɴ\n`{filename}`\n`{filesize}`\n`{caption}`"},
    "AUTO_DELETE_TIME": {"name": "ᴀᴜᴛᴏ ᴅᴇʟᴇᴛᴇ ᴛɪᴍᴇ", "help": "ᴛɪᴍᴇ ɪɴ (sᴇᴄᴏɴᴅs) ғᴏʀ ᴀᴜᴛᴏ-ᴅᴇʟᴇᴛᴇ."},
    "ENABLE_FSUB": {"name": "ᴇɴᴀʙʟᴇ ғᴏʀᴄᴇ sᴜʙ", "help": "ᴄʜᴀɴɢᴇ ғᴏʀᴄᴇ-sᴜʙ ᴍᴏᴅᴇ"},
    "VERIFICATION_MODE": {"name": "ᴠᴇʀɪғɪᴄᴀᴛɪᴏɴ ᴍᴏᴅᴇ", "help": "ᴄʜᴀɴɢᴇ ᴠᴇʀɪғɪᴄᴀᴛɪᴏɴ ᴍᴏᴅᴇ."},
    "AUTO_DELETE": {"name": "ᴀᴜᴛᴏ ᴅᴇʟᴇᴛᴇ", "help": "ᴄʜᴀɴɢᴇ ᴀᴜᴛᴏ-ᴅᴇʟᴇᴛᴇ ᴍᴏᴅᴇ."},
    "LOG_CHANNEL": {"name": "ʟᴏɢ ᴄʜᴀɴɴᴇʟ", "help": "ꜱᴇᴛ ʟᴏɢ ᴄʜᴀɴɴᴇʟ ɪᴅ ᴀɴᴅ ᴍᴀᴋᴇ ꜱᴜʀᴇ ʙᴏᴛ ɪꜱ ᴀᴅᴍɪɴ ᴏɴ ᴄʜᴀɴɴᴇʟ."},
    "PROTECT_CONTENT": {"name": "ᴘʀᴏᴛᴇᴄᴛ ᴄᴏɴᴛᴇɴᴛ", "help": "ʀᴇꜱᴛʀɪᴄᴛ ᴜꜱᴇʀ ꜰʀᴏᴍ ꜱᴀᴠɪɴɢ ᴄᴏɴᴛᴇɴᴛ."},
    "CLONE_BUTTON": {"name": "ᴄʟᴏɴᴇ ʙᴜᴛᴛᴏɴ", "help": "ꜱʜᴏᴡ ᴄʀᴇᴀᴛᴇ ᴄʟᴏɴᴇ ʙᴜᴛᴛᴏɴ ᴏɴ ʏᴏᴜʀ ʙᴏᴛ."},
    "PUBLIC_BOT": {"name": "ᴘᴜʙʟɪᴄ ʙᴏᴛ", "help": "ᴇᴠᴇʀʏᴏɴᴇ ᴄᴀɴ ᴜꜱᴇ ʙᴏᴛ."},
    "DEKOY": {"name": "DEKOY ʙᴏᴛ", "help": "DEKOY ᴄᴀɴ ᴜꜱᴇ ʙᴏᴛ."}

    
    
    
}

# ---------------- GROUPS ----------------
GROUP_KEYS = {
    "☉ ʀᴇQᴜɪʀᴇᴅ sᴇᴛᴛɪɴɢs": "required",
    "⍟ ᴀᴅᴍɪɴs": "admins",
    "⊛ ғᴏʀᴄᴇ sᴜʙ": "fsub",
    "⊘ ᴠᴇʀɪғɪᴄᴀᴛɪᴏɴ": "verification",
    "⌬ ᴀᴜᴛᴏ ᴅᴇʟᴇᴛᴇ": "autodelete",
    "○ ᴄᴀᴘᴛɪᴏɴ": "caption",
    "• ᴏᴛʜᴇʀ ꜱᴇᴛᴛɪɴɢꜱ": "other"
}

GROUPS = {
    "☉ ʀᴇQᴜɪʀᴇᴅ sᴇᴛᴛɪɴɢs": ["BOT_TOKEN", "DB_NAME"],
    "⍟ ᴀᴅᴍɪɴs": ["ADMINS"],
    "⊛ ғᴏʀᴄᴇ sᴜʙ": ["ENABLE_FSUB", "FSUB"],
    "⊘ ᴠᴇʀɪғɪᴄᴀᴛɪᴏɴ": [],
    "⌬ ᴀᴜᴛᴏ ᴅᴇʟᴇᴛᴇ": ["AUTO_DELETE", "AUTO_DELETE_TIME"],
    "○ ᴄᴀᴘᴛɪᴏɴ": ["CAPTION"],
    "• ᴏᴛʜᴇʀ ꜱᴇᴛᴛɪɴɢꜱ": [
        "PROTECT_CONTENT", "CLONE_BUTTON",
        "PUBLIC_BOT", "LOG_CHANNEL","DEKOY"
    ]
}

VERIFICATION_SUB = [
    "VERIFICATION_MODE",
    "PREMIUM_HOURS_VERIFICATION",
    "SHORTENER_DOMAIN",
    "SHORTENER_API_KEY"
]


# ---------------- KEYBOARDS ----------------
def get_group_keyboard():
    buttons = [
        [InlineKeyboardButton(name, callback_data=f"group:{key}")]
        for name, key in GROUP_KEYS.items()
    ]
    buttons.append([InlineKeyboardButton("⊗ ᴄʟᴏsᴇ", callback_data="close")])
    return InlineKeyboardMarkup(buttons)


def get_variable_keyboard(group_key: str):
    group_name = next(n for n, k in GROUP_KEYS.items() if k == group_key)

    if group_name == "⊘ ᴠᴇʀɪғɪᴄᴀᴛɪᴏɴ":
        vars_list = VERIFICATION_SUB
    else:
        vars_list = GROUPS[group_name]

    btns = [
        [InlineKeyboardButton(f"• {VARIABLE_INFO[v]['name']} •",
                              callback_data=f"setting:{group_key}:{v}")]
        for v in vars_list
    ]

    btns.append([
        InlineKeyboardButton("⊖ ʙᴀᴄᴋ", callback_data="back_to_groups"),
        InlineKeyboardButton("⊗ ᴄʟᴏsᴇ", callback_data="close")
    ])
    return InlineKeyboardMarkup(btns)


def get_setting_keyboard(group_key: str, var_name: str, is_boolean=False):
    if is_boolean:
        btns = [[InlineKeyboardButton(
            "✧ ᴏɴ / ᴏғғ",
            callback_data=f"toggle:{group_key}:{var_name}"
        )]]
    else:
        btns = [[InlineKeyboardButton(
            "✎ ᴇᴅɪᴛ",
            callback_data=f"edit:{group_key}:{var_name}"
        )]]

    btns.append([
        InlineKeyboardButton("⊖ ʙᴀᴄᴋ",
                             callback_data=f"back_to_group:{group_key}"),
        InlineKeyboardButton("⊗ ᴄʟᴏsᴇ", callback_data="close")
    ])
    return InlineKeyboardMarkup(btns)


# ---------------- HANDLERS ----------------
@Client.on_message(filters.command("settings") & filters.private)
async def settings_handler(client, message):
    await message.reply_text(
        "⚙️ <b>ʙᴏᴛ sᴇᴛᴛɪɴɢs</b>\n\nsᴇʟᴇᴄᴛ ᴀ ᴄᴀᴛᴇɢᴏʀʏ:",
        reply_markup=get_group_keyboard(),
        parse_mode=ParseMode.HTML
    )


@Client.on_callback_query(filters.regex(r"^group:(.+)"))
async def open_group(client, cq):
    group_key = cq.data.split(":")[1]
    group_name = next(n for n, k in GROUP_KEYS.items() if k == group_key)

    await cq.message.edit_text(
        f"📂 <b>{group_name}</b>\n\nSelect a variable:",
        reply_markup=get_variable_keyboard(group_key),
        parse_mode=ParseMode.HTML
    )


@Client.on_callback_query(filters.regex(r"^setting:(.+?):(.+)"))
async def open_setting(client, cq):
    group_key, var_name = cq.data.split(":")[1:]

    user = users_col.find_one({"USER_ID": cq.from_user.id}) or {}
    current = user.get(var_name, "Not set")
    info = VARIABLE_INFO.get(var_name, {"name": var_name, "help": ""})

    text = (f"<b>{info['name']}</b>\n\n"
            f"<b>Current:</b>\n<code>{current}</code>\n\n"
            f"{info['help']}")

    await cq.message.edit_text(
        text,
        reply_markup=get_setting_keyboard(
            group_key, var_name, var_name in BOOLEAN_VARS
        ),
        parse_mode=ParseMode.HTML
    )


@Client.on_callback_query(filters.regex(r"^toggle:(.+?):(.+)"))
async def toggle_setting(client, cq):
    group_key, var_name = cq.data.split(":")[1:]

    user = users_col.find_one({"USER_ID": cq.from_user.id}) or {}
    new_value = not bool(user.get(var_name, False))

    users_col.update_one(
        {"USER_ID": cq.from_user.id},
        {"$set": {var_name: new_value}}
    )

    await open_setting(client, cq)


@Client.on_callback_query(filters.regex(r"^edit:(.+?):(.+)"))
async def edit_setting(client, cq):
    group_key, var_name = cq.data.split(":")[1:]
    info = VARIABLE_INFO.get(var_name, {"name": var_name, "help": ""})

    await cq.message.edit_text(
        f"✎ Send new value for <b>{info['name']}</b>\n\n"
        f"{info['help']}\n\n⏳ Timeout: 120s",
        parse_mode=ParseMode.HTML
    )

    try:
        resp = await client.ask(
            cq.message.chat.id,
            text="Send value:",
            timeout=120
        )

        new_value = int(resp.text.strip()) if var_name in INT_VARS else resp.text.strip()

        users_col.update_one(
            {"USER_ID": cq.from_user.id},
            {"$set": {var_name: new_value}}
        )

        await cq.message.reply_text(
            f"✅ Updated <b>{info['name']}</b>:\n<code>{new_value}</code>",
            parse_mode=ParseMode.HTML
        )

    except asyncio.TimeoutError:
        await cq.message.reply_text("⏳ Edit timed out.", parse_mode=ParseMode.HTML)

    await open_setting(client, cq)


# ---------------- BACK BUTTONS ----------------
@Client.on_callback_query(filters.regex(r"^back_to_groups$"))
async def back_to_groups(client, cq):
    await cq.message.edit_text(
        "⚙️ <b>ʙᴏᴛ sᴇᴛᴛɪɴɢs</b>\n\nsᴇʟᴇᴄᴛ ᴀ ᴄᴀᴛᴇɢᴏʀʏ:",
        reply_markup=get_group_keyboard(),
        parse_mode=ParseMode.HTML
    )


@Client.on_callback_query(filters.regex(r"^back_to_group:(.+)"))
async def back_to_group(client, cq):
    group_key = cq.data.split(":")[1]
    group_name = next(n for n, k in GROUP_KEYS.items() if k == group_key)

    await cq.message.edit_text(
        f"📂 <b>{group_name}</b>\n\nSelect a variable:",
        reply_markup=get_variable_keyboard(group_key),
        parse_mode=ParseMode.HTML
    )


@Client.on_callback_query(filters.regex(r"^close$"))
async def close_menu(client, cq):
    await cq.message.delete()