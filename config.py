# config.py

import os
 # This is for Code 1 (filestore bot)


# ---------------------------
# Code 1 (Filestore Bot) Config
# ---------------------------

BOT_TOKEN = CONFIG.get("BOT_TOKEN")
API_ID = CONFIG.get("API_ID")
API_HASH = CONFIG.get("API_HASH")
MONGO_URI = CONFIG.get("MONGO_URI")
DB_NAME = CONFIG.get("DB_NAME", "filestore_clone")

ADMINS = CONFIG.get("ADMINS", [])
ENABLE_FSUB = CONFIG.get("ENABLE_FSUB", False)
FSUB = CONFIG.get("FSUB")

VERIFICATION_MODE = CONFIG.get("VERIFICATION_MODE", False)
PREMIUM_HOURS_VERIFICATION = CONFIG.get("PREMIUM_HOURS_VERIFICATION", 8)
VERIFY_SLUG_TTL_HOURS = CONFIG.get("VERIFY_SLUG_TTL_HOURS", 48)

SHORTENER_DOMAIN = CONFIG.get("SHORTENER_DOMAIN", "")
SHORTENER_API = CONFIG.get("SHORTENER_API_KEY")
CAPTION = CONFIG.get("CAPTION", "📄{caption}")


# ---------------------------
# Code 2 (Clone Maker Bot) Config
# ---------------------------

CODE2_BOT_TOKEN = os.getenv("CODE2_BOT_TOKEN", "7630512584:AAEAnpDk4dW7Xa9TGEIZ3C37k6CicN7bAnA")
CODE2_API_ID = int(os.getenv("CODE2_API_ID", "15191874"))
CODE2_API_HASH = os.getenv("CODE2_API_HASH", "3037d39233c6fad9b80d83bb8a339a07")
CODE2_MONGO_URI = os.getenv("CODE2_MONGO_URI", "mongodb+srv://hp108044:zWy9AuflXmsrAfSY@cluster0.zlecn7m.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
CODE2_DB_NAME = os.getenv("CODE2_DB_NAME", "clone_maker")

CODE2_ADMINS = list(map(int, os.getenv("CODE2_ADMINS", "5597521952").split(",")))