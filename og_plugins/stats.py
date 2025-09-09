from pyrogram import Client, filters
from db_config import users_col
import psutil
import shutil
import time

# Record bot start time for uptime calculation
START_TIME = time.time()

@Client.on_message(filters.command("stats") & filters.private)
async def stats_handler(client, message):
    total_users = users_col.count_documents({})
    active_deployments = users_col.count_documents({"BOT_STATUS": "running"})
    log_channel_users = users_col.count_documents({"LOG_CHANNEL_ID": {"$exists": True, "$ne": None}})
    
    cpu_usage = psutil.cpu_percent(interval=1)
    memory = psutil.virtual_memory()
    mem_used_gb = memory.used / (1024 ** 3)
    mem_total_gb = memory.total / (1024 ** 3)
    mem_percent = memory.percent

    disk = shutil.disk_usage("/")
    disk_used_gb = disk.used / (1024 ** 3)
    disk_total_gb = disk.total / (1024 ** 3)
    disk_percent = (disk.used / disk.total) * 100

    uptime_seconds = int(time.time() - START_TIME)
    uptime_hours, remainder = divmod(uptime_seconds, 3600)
    uptime_minutes, _ = divmod(remainder, 60)

    stats_message = (
        "📊 *Bot System Statistics*\n\n"
        f"👥 Total Users: *{total_users}*\n"
        f"🚀 Active Deployments: *{active_deployments}*\n"
        f"🔔 Users with LOG_CHANNEL_ID: *{log_channel_users}*\n\n"
        f"⚙️ CPU Usage: *{cpu_usage}%*\n"
        f"💾 Memory Usage: *{mem_used_gb:.1f} GB / {mem_total_gb:.1f} GB ({mem_percent}%) *\n"
        f"📂 Disk Usage: *{disk_used_gb:.1f} GB / {disk_total_gb:.1f} GB ({disk_percent:.1f}%) *\n\n"
        f"⏱️ Uptime: *{uptime_hours} hours {uptime_minutes} minutes*"
    )

    await message.reply_text(stats_message, parse_mode="markdown")