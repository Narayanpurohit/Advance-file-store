import logging
import datetime
from bot import PREMIUM_HOURS_VERIFICATION, VERIFY_SLUG_TTL_HOURS
from database import create_verification_slug, use_verification_slug, add_premium_hours
from .shortener import shorten_url

log = logging.getLogger(__name__)


# Handle verification when user clicks the start link
async def start_verification_flow(client, message, slug):
    user_id = message.from_user.id
    try:
        record = use_verification_slug(slug)  # Returns full doc or None
    except Exception as e:
        log.exception(f"🔥 DB error while using verification slug {slug} for user {user_id}: {e}")
        await message.reply_text(f"⚠️ Verification error: {e}")
        return

    if not record:
        # Handle old timestamp-based slugs with a dot (backward compatibility)
        if slug.startswith("verify_") and "." in slug:
            log.warning(f"❌ Expired old-style verification slug {slug} used by {user_id}")
            await message.reply_text("❌ This old verification link has expired. Please request a new one.")
        else:
            log.warning(f"❌ Invalid or expired verification slug {slug} attempted by {user_id}")
            await message.reply_text("❌ Invalid or expired verification link.")
        return

    # Check if slug belongs to this user
    if record.get("user_id") != user_id:
        log.warning(f"⚠️ User {user_id} attempted to use slug belonging to {record.get('user_id')}")
        await message.reply_text("⚠️ This verification link is not for your account.")
        return

    # Give premium hours
    try:
        add_premium_hours(user_id, PREMIUM_HOURS_VERIFICATION)
        log.info(f"✅ User {user_id} verified successfully. Premium added for {PREMIUM_HOURS_VERIFICATION} hours.")
        await message.reply_text(
            f"✅ Verified! You now have premium for {PREMIUM_HOURS_VERIFICATION} hours."
        )
    except Exception as e:
        log.exception(f"⚠️ Failed to apply premium for user {user_id}: {e}")
        await message.reply_text(f"⚠️ Failed to apply premium: {e}")


# Create and send verification link to user
async def send_verification_link(client, user_id):
    try:
        slug = create_verification_slug(user_id, VERIFY_SLUG_TTL_HOURS)  # user_id stored with slug
        bot_link = f"https://t.me/{client.me.username}?start={slug}"

        # Pass bot link through shortener
        try:
            short_link = shorten_url(bot_link)
        except Exception as e:
            log.error(f"⚠️ Shortener failed for user {user_id}, using raw link. Error: {e}")
            short_link = bot_link

        await client.send_message(
            user_id,
            f"⚠️ Please verify to continue:\n\n{short_link}"
        )
        log.info(f"🔗 Verification link sent to user {user_id}: {slug}")
    except Exception as e:
        log.exception(f"❌ Could not generate/send verification link for user {user_id}: {e}")
        await client.send_message(user_id, f"❌ Could not generate verification link: {e}")