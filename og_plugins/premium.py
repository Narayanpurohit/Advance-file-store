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

>🎉 ᴀʟʟ ᴘʀɪᴄᴇ ʟɪꜱᴛ 🎉
>
>🔅 𝟮𝟬𝟬𝟬 ᴘᴛꜱ : **𝟰𝟬 ʀꜱ**  
>🔅 𝟰𝟬𝟬𝟬 ᴘᴛꜱ : **𝟴𝟬 ʀꜱ**  
>🔅 𝟭𝟬𝟬𝟬𝟬 ᴘᴛꜱ : **𝟭𝟮𝟬 ʀꜱ** 

ᴄᴏᴘʏ ᴛʜɪꜱ ᴜᴘɪ ɪᴅ  
ᴜᴘɪ ɪᴅ ➢`narayanpurohit444@axl`

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
    
    




@Client.on_message(filters.command("addpoints") & filters.user(CODE2_ADMINS))
async def add_points(client, message):
    try:
        args = message.text.split()
        if len(args) != 3:
            return await message.reply_text("Usage: /addpoints <user_id> <amount>")

        user_id = int(args[1])
        amount = int(args[2])

        user = users_col.find_one({"USER_ID": user_id})
        if not user:
            return await message.reply_text("❌ User not found.")

        # Convert PREMIUM_POINTS to int if it is a string
        if isinstance(user.get("PREMIUM_POINTS"), str):
            users_col.update_one(
                {"USER_ID": user_id},
                [{"$set": {"PREMIUM_POINTS": {"$toInt": "$PREMIUM_POINTS"}}}]
            )

        # Add points
        result = users_col.find_one_and_update(
            {"USER_ID": user_id},
            {"$inc": {"PREMIUM_POINTS": amount}},
            return_document=True
        )

        await message.reply_text(
            f"✅ Added **{amount} points** to user `{user_id}`.\n"
            f"⭐ New total: **{result.get('PREMIUM_POINTS', 0)} points**"
        )

    except Exception as e:
        await message.reply_text(f"⚠️ Error: {e}")