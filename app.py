import logging
from pyrogram import Client
import config

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s"
)

log = logging.getLogger("CloneMakerBot")

app = Client(
    "clone-maker-bot",
    api_id=config.API_ID,
    api_hash=config.API_HASH,
    bot_token=config.CLONE_BOT_TOKEN,   # ⚠️ New token in config
    plugins=dict(root="og_plugins")
)

if __name__ == "__main__":
    log.info("🚀 Clone Maker Bot starting...")
    app.run()