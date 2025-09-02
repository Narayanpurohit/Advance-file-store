import datetime
import logging
from pyrogram import Client, filters
from database import users_col, stats_col, files_col

log = logging.getLogger(__name__)


def get_total_users():
    count = users_col.count_documents({})
    log.debug(f"📊 get_total_users → {count}")
    return count


def get_premium_users():
    now = datetime.datetime.utcnow()
    count = users_col.count_documents({"premium_until": {"$gt": now}})
    log.debug(f"📊 get_premium_users → {count}")
    return count


def get_total_files_sent():
    doc = stats_col.find_one({"_id": "stats"})
    value = doc.get("files_sent", 0) if doc else 0
    log.debug(f"📊 get_total_files_sent → {value}")
    return value


def get_total_batches_sent():
    doc = stats_col.find_one({"_id": "stats"})
    value = doc.get("batches_sent", 0) if doc else 0
    log.debug(f"📊 get_total_batches_sent → {value}")
    return value


def get_total_batch_messages_sent():
    doc = stats_col.find_one({"_id": "stats"})
    value = doc.get("batch_messages_sent", 0) if doc else 0
    log.debug(f"📊 get_total_batch_messages_sent → {value}")
    return value


@Client.on_message(filters.command("stats") & filters.private)
async def stats_handler(client, message):
    try:
        user_id = message.from_user.id
        log.info(f"📥 /stats command requested by {user_id}")

        total_users = get_total_users()
        premium_users = get_premium_users()
        total_files_stored = files_col.count_documents({})
        total_files_sent = get_total_files_sent()
        total_batches_sent = get_total_batches_sent()
        total_batch_messages_sent = get_total_batch_messages_sent()

        text = (
            f"📊 **Bot Stats** 📊\n\n"
            f"👥 Total Users: `{total_users}`\n"
            f"⭐ Premium Users: `{premium_users}`\n"
            f"📁 Total Files Stored: `{total_files_stored}`\n"
            f"📂 Files Sent: `{total_files_sent}`\n"
            f"📦 Batches Sent: `{total_batches_sent}`\n"
            f"🗂️ Batch Messages Sent: `{total_batch_messages_sent}`"
        )

        await message.reply_text(text)
        log.info(
            f"✅ Stats sent to {user_id} → Users={total_users}, Premium={premium_users}, "
            f"FilesStored={total_files_stored}, FilesSent={total_files_sent}, "
            f"BatchesSent={total_batches_sent}, BatchMsgsSent={total_batch_messages_sent}"
        )

    except Exception as e:
        log.exception(f"🔥 Error in /stats handler: {e}")
        await message.reply_text("⚠️ Failed to fetch stats. Please try again later.")