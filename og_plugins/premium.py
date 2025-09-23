from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from db_config import users_col
from config import CODE2_ADMINS


@Client.on_message(filters.command("points") & filters.private)
async def premium_handler(client, message):
    user_id = message.from_user.id
    user = users_col.find_one({"USER_ID": user_id}) or {}
    points = user.get("PREMIUM_POINTS", 0)

    buttons = InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("• ʙᴜʏ ᴘᴏɪɴᴛꜱ •", callback_data="buy_points")]
        ]
    )

    await message.reply_text(
        f"⭐ ʏᴏᴜ ᴄᴜʀʀᴇɴᴛʟʏ ʜᴀᴠᴇ **{points} ᴘᴏɪɴᴛꜱ**.",
        reply_markup=buttons
    )

@Client.on_callback_query(filters.regex("buy_points"))
async def buy_points_callback(client, callback_query):
    text = """💰💳 ʜᴇʏ ᴘʀᴇᴍɪᴜᴍ ᴘʟᴀɴꜱ 💲
**• ꜰɪʟᴇ ꜱᴛᴏʀᴇ ʙᴏᴛ ꜰᴇᴀᴛᴜʀᴇ**

࣭ ⭑⚝ ᴠᴇʀɪꜰɪᴄᴀᴛɪᴏɴ ᴍᴏᴅᴇ  
࣭ ⭑⚝ ᴄᴜꜱᴛᴏᴍ ꜱʜᴏʀᴛɴᴇʀ ꜱᴜᴘᴘᴏʀᴛ  
࣭ ⭑⚝ ᴄᴜꜱᴛᴏᴍ ᴠᴇʀɪꜰɪᴄᴀᴛɪᴏɴ ʜᴏᴜʀ  
࣭ ⭑⚝ ꜰꜱᴜʙ ᴍᴏᴅᴇ  
࣭ ⭑⚝ ᴜɴʟɪᴍɪᴛᴇᴅ ꜰꜱᴜʙ ᴄʜᴀɴɴᴇʟ  
࣭ ⭑⚝ ᴄᴜꜱᴛᴏᴍ ꜰɪʟᴇ ᴄᴀᴘᴛɪᴏɴ  
࣭ ⭑⚝ ꜱᴜᴘᴘᴏʀᴛ ʙʀᴏᴀᴅᴄᴀꜱᴛ  
࣭ ⭑⚝ ᴜꜱᴇʀ ꜱᴛᴀᴛꜱ  

”🎉 ᴀʟʟ ᴘʀɪᴄᴇ ʟɪꜱᴛ 🎉

🔅 𝟮𝟬𝟬𝟬 ᴘᴛꜱ : **𝟰𝟬 ʀꜱ**  
🔅 𝟰𝟬𝟬𝟬 ᴘᴛꜱ : **𝟴𝟬 ʀꜱ**  
🔅 𝟭𝟬𝟬𝟬𝟬 ᴘᴛꜱ : **𝟭𝟮𝟬 ʀꜱ**  ”

ᴄᴏᴘʏ ᴛʜɪꜱ ᴜᴘɪ ɪᴅ  
ᴜᴘɪ ɪᴅ ➢

**ᴛᴀᴘ ᴛᴏ ᴄᴏᴘʏ  **

ꜰᴏʀ ᴄʟᴏɴᴇ ᴍᴀᴋᴇʀ ʙᴏᴛ'ꜱ ꜰᴇᴀᴛᴜʀᴇꜱ ʟɪꜱᴛ /ʜᴇʟᴘ  

⚠️ ꜱᴇɴᴅ ꜱꜱ ᴀꜰᴛᴇʀ ᴘᴀʏᴍᴇɴᴛ ⚠️  
ᴀꜰᴛᴇʀ ꜱᴇɴᴅɪɴɢ ᴀ ꜱᴄʀᴇᴇɴꜱʜᴏᴛ ᴘʟᴇᴀꜱᴇ ɢɪᴠᴇ ᴜꜱ ꜱᴏᴍᴇ ᴛɪᴍᴇ ᴛᴏ ᴀᴅᴅ ʏᴏᴜ ɪɴ ᴛʜᴇ ᴘʀᴇᴍɪᴜᴍ ᴠᴇʀꜱɪᴏɴ｡｡"""

    buttons = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("• ꜱᴇɴᴅ ꜱᴄʀᴇᴇɴꜱʜᴏᴛꜱ •", url="https://t.me/jn_dev")
            ],
            [
                InlineKeyboardButton("• ʙᴀᴄᴋ •", callback_data="back_to_points")
            ]
        ]
    )

    await callback_query.message.edit(text=text, reply_markup=buttons)

@Client.on_callback_query(filters.regex("back_to_points"))
async def back_to_points_callback(client, callback_query):
    user_id = callback_query.from_user.id
    user = users_col.find_one({"USER_ID": user_id}) or {}
    points = user.get("PREMIUM_POINTS", 0)

    buttons = InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("• ʙᴜʏ ᴘᴏɪɴᴛꜱ •", callback_data="buy_points")]
        ]
    )

    await callback_query.message.edit(
        f"⭐ ʏᴏᴜ ᴄᴜʀʀᴇɴᴛʟʏ ʜᴀᴠᴇ **{points} ᴘᴏɪɴᴛꜱ**.",
        reply_markup=buttons
    )
    
    


@Client.on_message(filters.command("addpoints") & filters.private)
async def add_points_handler(client, message):
    if message.from_user.id not in ADMINS:
        await message.reply_text("🚫 ʏᴏᴜ ᴀʀᴇ ɴᴏᴛ ᴀᴜᴛʜᴏʀɪᴢᴇᴅ ᴛᴏ ᴜꜱᴇ ᴛʜɪꜱ ᴄᴏᴍᴍᴀɴᴅ.")
        return

    args = message.text.split()
    if len(args) != 3:
        await message.reply_text("⚠️ ᴜꜱᴀɢᴇ:\n`/addpoints <user_id> <points>`")
        return

    try:
        user_id = int(args[1])
        points_to_add = int(args[2])
    except ValueError:
        await message.reply_text("⚠️ ᴜꜱᴇʀ_ɪᴅ ᴀɴᴅ ᴘᴏɪɴᴛꜱ ᴍᴜꜱᴛ ʙᴇ ɴᴜᴍʙᴇʀꜱ.")
        return

    result = users_col.find_one_and_update(
        {"USER_ID": user_id},
        {"$inc": {"PREMIUM_POINTS": points_to_add}},
        upsert=True,
        return_document=True
    )

    new_points = result.get("PREMIUM_POINTS", 0)

    await message.reply_text(
        f"✅ ᴀᴅᴅᴇᴅ **{points_to_add} ᴘᴏɪɴᴛꜱ** ᴛᴏ ᴜꜱᴇʀ `{user_id}`.\n"
        f"🌟 ɴᴇᴡ ʙᴀʟᴀɴᴄᴇ: **{new_points} ᴘᴏɪɴᴛꜱ**"
    )

