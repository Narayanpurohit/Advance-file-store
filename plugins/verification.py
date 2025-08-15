import requests
from config import PREMIUM_HOURS_VERIFICATION, VERIFY_SLUG_TTL_HOURS, SHORTENER_API_KEY, SHORTENER_API_BASE
from database import create_verification_slug, use_verification_slug, add_premium_hours


# Shorten the verification link using API (if configured)
def shorten_url(url):
    if SHORTENER_API_BASE and SHORTENER_API_KEY:
        try:
            resp = requests.post(
                SHORTENER_API_BASE,
                json={"url": url},
                headers={"Authorization": f"Bearer {SHORTENER_API_KEY}"}
            )
            data = resp.json()
            return data.get("shortenedUrl") or url
        except Exception as e:
            print(f"Shortener error: {e}")
            return url
    return url


# Handle verification when user clicks the start link
async def start_verification_flow(client, message, slug):
    record = use_verification_slug(slug)  # Returns full doc or None
    if not record:
        await message.reply_text("❌ Invalid or expired verification link.")
        return

    # Check if slug belongs to this user
    if record["user_id"] != message.from_user.id:
        await message.reply_text("⚠️ This verification link is not for your account.")
        return

    # Give premium
    add_premium_hours(message.from_user.id, PREMIUM_HOURS_VERIFICATION)
    await message.reply_text(f"✅ Verified! You now have premium for {PREMIUM_HOURS_VERIFICATION} hours.")


# Create and send verification link to user
async def send_verification_link(client, user_id):
    slug = create_verification_slug(user_id, VERIFY_SLUG_TTL_HOURS)  # user_id stored with slug
    bot_link = f"https://t.me/{client.me.username}?start={slug}"
    short_link = shorten_url(bot_link)
    await client.send_message(
        user_id,
        f"⚠️ Please verify to continue:\n\n{short_link}"
    )