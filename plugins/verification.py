import datetime
from bot import PREMIUM_HOURS_VERIFICATION, VERIFY_SLUG_TTL_HOURS
from database import create_verification_slug, use_verification_slug, add_premium_hours
from .shortener import shorten_url


# Handle verification when user clicks the start link
async def start_verification_flow(client, message, slug):
    try:
        record = use_verification_slug(slug)  # Returns full doc or None
    except Exception as e:
        await message.reply_text(f"⚠️ Verification error: {e}")
        return

    if not record:
        # Handle old timestamp-based slugs with a dot (backward compatibility)
        if slug.startswith("verify_") and "." in slug:
            await message.reply_text("❌ This old verification link has expired. Please request a new one.")
        else:
            await message.reply_text("❌ Invalid or expired verification link.")
        return

    # Check if slug belongs to this user
    if record.get("user_id") != message.from_user.id:
        await message.reply_text("⚠️ This verification link is not for your account.")
        return

    # Give premium hours
    try:
        add_premium_hours(message.from_user.id, PREMIUM_HOURS_VERIFICATION)
        await message.reply_text(
            f"✅ Verified! You now have premium for {PREMIUM_HOURS_VERIFICATION} hours."
        )
    except Exception as e:
        await message.reply_text(f"⚠️ Failed to apply premium: {e}")


# Create and send verification link to user
async def send_verification_link(client, user_id):
    try:
        slug = create_verification_slug(user_id, VERIFY_SLUG_TTL_HOURS)  # user_id stored with slug
        bot_link = f"https://t.me/{client.me.username}?start={slug}"

        # Pass bot link through shortener
        short_link = shorten_url(bot_link)

        await client.send_message(
            user_id,
            f"⚠️ Please verify to continue:\n\n{short_link}\n\n{bot_link}"
        )
    except Exception as e:
        await client.send_message(user_id, f"❌ Could not generate verification link: {e}")