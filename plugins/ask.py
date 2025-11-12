# ask.py
import asyncio
from pyrogram import Client
from pyrogram.types import Message

# Global dictionary to track pending replies
PENDING_ASKS = {}  # key = user_id, value = asyncio.Future


async def ask(client: Client, user_id: int, question: str, timeout: int = 120):
    """
    Ask a question to the user and wait for their reply.
    Returns the reply Message object.
    Raises asyncio.TimeoutError if user doesn't reply in time.
    """
    await client.send_message(user_id, question)

    loop = asyncio.get_event_loop()
    future = loop.create_future()
    PENDING_ASKS[user_id] = future

    try:
        message = await asyncio.wait_for(future, timeout=timeout)
        return message
    finally:
        if user_id in PENDING_ASKS:
            del PENDING_ASKS[user_id]


@Client.on_message()
async def _capture_reply(client: Client, message: Message):
    """
    Captures private user replies and resolves pending asks.
    """
    if not message.from_user:
        return
    user_id = message.from_user.id

    if user_id in PENDING_ASKS:
        future = PENDING_ASKS.pop(user_id)
        if not future.done():
            future.set_result(message)