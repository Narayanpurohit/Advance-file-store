from pyrogram import Client, filters
from db_config import users_col
import psutil
import shutil
import time
from datetime import datetime, timedelta

START_TIME = time.time()

def format_uptime(seconds: int) -> str:
    uptime = timedelta(seconds=seconds)
    days = uptime.days
    hours, remainder = divmod(uptime.seconds, 3600)
    minutes, _ = divmod(remainder, 60)
    parts = []
    if days:
        parts.append(f"{days}d")
    if hours:
        parts.append(f"{hours}h")
    if minutes:
        parts.append(f"{minutes}m")
    return " ".join(parts) if parts else "0m"

@Client.on_message(filters.command("stats") & filters.private)
async def stats_handler(client, message):
    total_users = users_col.count_documents({})
    active_deployments = users_col.count_documents({"BOT_STATUS": "running"})
    users_with_log_channel = users_col.count_documents({"LOG_CHANNEL_ID": {"$exists": True}})
    
    cpu_usage = psutil.cpu_percent(interval=1)
    mem = psutil.virtual_memory()
    mem_used = round(mem.used / 1024 / 1024, 2)
    mem_total = round(mem.total / 1024 / 1024, 2)
    mem_percent = mem.percent

    disk = shutil.disk_usage("/")
    disk_used = round(disk.used / 1024 / 1024 / 1024, 2)
    disk_total = round(disk.total / 1024 / 1024 / 1024, 2)
    disk_percent = round((disk.used / disk.total) * 100, 2)

    uptime_seconds = int(time.time() - START_TIME)
    uptime_str = format_uptime(uptime_seconds)

    stats_message = (
        "📊 **Bot System Statistics**\n\n"
        f"👥 **Total Users:** `{total_users}`\n"
        f"🚀 **Active Deployments:** `{active_deployments}`\n"
        f"🔔 **Users with LOG Channel:** `{users_with_log_channel}`\n\n"
        f"⚙️ **CPU Usage:** `{cpu_usage}%`\n"
        f"💾 **Memory Usage:** `{mem_used} MB / {mem_total} MB ({mem_percent}%)`\n"
        f"📂 **Disk Usage:** `{disk_used} GB / {disk_total} GB ({disk_percent}%)`\n\n"
        f"⏱️ **Uptime:** `{uptime_str}`"
    )

    await message.reply_text(stats_message)