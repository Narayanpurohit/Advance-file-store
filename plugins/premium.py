from pyrogram import Client, filters
from bot import ADMINS
from database import add_premium_days, remove_premium, get_premium_expiry
import datetime


@Client.on_message(filters.command("add_premium") & filters.user(ADMINS))
async def cmd_add_premium(client, message):
    """
    Admin: /add_premium <user_id> <days>
    Gives premium for the specified number of days.
    """
    try:
        parts = message.text.split()
        if len(parts) != 3:
            await message.reply_text("Usage: `/add_premium <user_id> <days>`", quote=True)
            return

        user_id = int(parts[1])
        days = int(parts[2])

        add_premium_days(user_id, days)
        await message.reply_text(f"✅ Added premium for {days} day(s) to user `{user_id}`.", quote=True)

    except Exception as e:
        await message.reply_text(f"❌ Error: `{e}`", quote=True)


@Client.on_message(filters.command("remove_premium") & filters.user(ADMINS))
async def cmd_remove_premium(client, message):
    """
    Admin: /remove_premium <user_id>
    Removes premium from a user.
    """
    try:
        parts = message.text.split()
        if len(parts) != 2:
            await message.reply_text("Usage: `/remove_premium <user_id>`", quote=True)
            return

        user_id = int(parts[1])
        remove_premium(user_id)
        await message.reply_text(f"❌ Premium removed from user `{user_id}`.", quote=True)

    except Exception as e:
        await message.reply_text(f"❌ Error: `{e}`", quote=True)


@Client.on_message(filters.command("mypremium") & filters.private)
async def cmd_my_premium(client, message):
    """
    User: /mypremium
    Shows remaining premium time.
    """
    try:
        user_id = message.from_user.id
        expiry = get_premium_expiry(user_id)

        if not expiry:
            await message.reply_text("❌ You do not have premium access.", quote=True)
            return

        now = datetime.datetime.utcnow()
        if expiry < now:
            await message.reply_text("❌ Your premium has expired.", quote=True)
            return

        remaining = expiry - now
        days = remaining.days
        hours = remaining.seconds // 3600
        minutes = (remaining.seconds % 3600) // 60

        await message.reply_text(
            f"✅ Your premium expires in **{days} days, {hours} hours, {minutes} minutes**.",
            quote=True
        )

    except Exception as e:
        await message.reply_text(f"❌ Error: `{e}`", quote=True)