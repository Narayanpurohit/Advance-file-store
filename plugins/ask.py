# ask.py
import asyncio
from pyrogram.types import Message
from pyrogram import Client, filters


async def ask(client: Client, user_id: int, question: str, timeout: int = 120) -> Message:
    """
    Ask a specific user a question and wait for their next message.
    Only triggers for that user in that moment.
    """

    await client.send_message(user_id, question)

    # Local filter — only accept next message from the same user in private chat
    user_filter = filters.private & filters.user(user_id)

    try:
        # Wait for a single message from the same user
        response: Message = await client.listen(filters=user_filter, timeout=timeout)
        return response
    except asyncio.TimeoutError:
        raise asyncio.TimeoutError("User did not reply in time.")