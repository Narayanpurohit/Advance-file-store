import random, string
from bot import BOT_USERNAME

await message.reply_text(f"Here is your link:\n{link}")
from pyrogram import Client, filters
from database import add_file
from config import BOT_USERNAME, ADMINS

def gen_slug(prefix):
    return prefix + ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))

@Client.on_message(filters.user(ADMINS) & (filters.video | filters.audio | filters.document))
async def handle_file(client, message):
    file_type = "vid" if message.video else "aud" if message.audio else "doc"
    file_id = message.video.file_id if message.video else message.audio.file_id if message.audio else message.document.file_id
    slug = gen_slug(file_type + "_")
    add_file(slug, file_id, file_type)
    link = f"https://t.me/{BOT_USERNAME}?start={slug}"
    await message.reply_text(f"✅ File saved!\n🔗 {link}")