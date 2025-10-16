from pyrogram import Client, filters

@Client.on_message(filters.command("stats"))
async def stats_handler(client, message):
    try:
        # Check if user is admin
        if message.from_user.id not in ADMINS:
            return await message.reply_text("❌ You need admin access to use this command.")

        # Normal stats logic for admins
        await message.reply_text(get_stats_text(), reply_markup=get_main_buttons())

    except Exception as e:
        log.exception(f"🔥 Error in /stats handler: {e}")
        await message.reply_text("⚠️ Failed to fetch stats. Please try again later.")


async def show_users_list(query, prefix, users):
    total_pages = (len(users) + PER_PAGE - 1) // PER_PAGE
    page = int(query.data.split("_")[-1])
    text = f"**{prefix.replace('_',' ').title()} List**\n\n" + get_user_list(users, page)
    await query.message.edit_text(text, reply_markup=get_list_buttons(page, total_pages, prefix))