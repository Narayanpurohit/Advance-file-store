from pyrogram import Client, filters
from db_config import users_col
import psutil
import shutil
import time
from datetime import datetime

START_TIME = time.time()

@Client.on_message(filters.command("stats") & filters.private)
async def stats_handler(client, message):
    total_users = users_col.count_documents({})
    active_deployments = users_col.count_documents({"BOT_STATUS": "running"})
    users_with_log = users_col.count_documents({"LOG_CHANNEL_ID": {"$exists": True}})

    cpu_percent = psutil.cpu_percent(interval=1)
    mem = psutil.virtual_memory()
    total_mem = round(mem.total / (1024 * 1024 * 1024), 2)
    used_mem = round(mem.used / (1024 * 1024 * 1024), 2)
    mem_percent = mem.percent

    disk = shutil.disk_usage("/")
    total_disk = round(disk.total / (1024 * 1024 * 1024), 2)
    used_disk = round(disk.used / (1024 * 1024 * 1024), 2)
    disk_percent = round((used_disk / total_disk) * 100, 2)

    uptime_seconds = int(time.time() - START_TIME)
    hours, remainder = divmod(uptime_seconds, 3600)
    minutes, _ = divmod(remainder, 60)
    uptime_str = f"{hours} hours {minutes} minutes"

    stats_message = f"""📊 Bot System Statistics

👥 Total Users: {total_users}
🚀 Active Deployments: {active_deployments}
🔔 Users with LOG_CHANNEL_ID: {users_with_log}

⚙️ CPU Usage: {cpu_percent}%
💾 Memory Usage: {used_mem} GB / {total_mem} GB ({mem_percent}%)
📂 Disk Usage: {used_disk} GB / {total_disk} GB ({disk_percent}%)

⏱️ Uptime: {uptime_str}
"""

    await message.reply_text(stats_message, parse_mode="md")