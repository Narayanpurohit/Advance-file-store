from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from db_config import users_col

@Client.on_message(filters.command("points") & filters.private)
async def premium_handler(client, message):
    user_id = message.from_user.id
    user = users_col.find_one({"USER_ID": user_id}) or {}
    points = user.get("points", 0)

    buttons = InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("💰 Buy Points", callback_data="buy_points")]
        ]
    )

    await message.reply_text(
        f"⭐ You currently have **{points} points**.",
        reply_markup=buttons
    )

@Client.on_callback_query(filters.regex("buy_points"))
async def buy_points_callback(client, callback_query):
    text = """💰💳𝐇𝐞𝐲 𝐏𝐫𝐞𝐦𝐢𝐮𝐦 𝐏𝐥𝐚𝐧𝐬 💲
• File store bot 𝗙𝗲𝗮𝘁𝘂𝗿𝗲

࣭ ⭑⚝ verification mode 
࣭ ⭑⚝ Custom shortner support 
࣭ ⭑⚝ Custom verification hour
࣭ ⭑⚝ Fsub mode
࣭ ⭑⚝ Unlimited Fsub channel 
࣭ ⭑⚝ Custom File caption 
࣭ ⭑⚝ Support broadcast 
࣭ ⭑⚝ user stats

𝗔𝗹𝗹 𝗣𝗿𝗶𝗰𝗲 𝗟𝗶𝘀𝘁

🔅2000 pts : 40 𝗿𝘀
🔅4000 pts : 80 𝗿𝘀
🔅10000 pts : 120 𝗿𝘀

ᴄᴏᴘʏ ᴛʜɪs ᴜᴘɪ ɪᴅ
ᴜᴘɪ ɪᴅ ➢

TAP TO COPY

For clone maker bot's features list /help

⚠️𝗦𝗲𝗻𝗱 𝗦𝗦 𝗔𝗳𝘁𝗲𝗿 𝗣𝗮𝘆𝗺𝗲𝗻𝘁⚠️ After sending a Screenshot please give us some time to add you in the premium version｡｡"""

    buttons = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("📸 Send Screenshots", url="https://t.me/jn_dev")
            ],
            [
                InlineKeyboardButton("🔙 Back", callback_data="back_to_points")
            ]
        ]
    )

    await callback_query.message.edit(text=text, reply_markup=buttons)

@Client.on_callback_query(filters.regex("back_to_points"))
async def back_to_points_callback(client, callback_query):
    user_id = callback_query.from_user.id
    user = users_col.find_one({"USER_ID": user_id}) or {}
    points = user.get("points", 0)

    buttons = InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("💰 Buy Points", callback_data="buy_points")]
        ]
    )

    await callback_query.message.edit(
        f"⭐ You currently have **{points} points**.",
        reply_markup=buttons
    )