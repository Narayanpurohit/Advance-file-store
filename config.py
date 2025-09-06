# config.py

import os
 # This is for Code 1 (filestore bot)


# ---------------------------
# Code 1 (Filestore Bot) Config
# ---------------------------

BOT_TOKEN =  ("BOT_TOKEN")
API_ID =  ("API_ID")
API_HASH =  ("API_HASH")
MONGO_URI =  ("MONGO_URI")
DB_NAME =  ("DB_NAME", "filestore_clone")

ADMINS =  ("ADMINS", [])
ENABLE_FSUB =  ("ENABLE_FSUB", False)
FSUB =  ("FSUB")

VERIFICATION_MODE =  ("VERIFICATION_MODE", False)
PREMIUM_HOURS_VERIFICATION =  ("PREMIUM_HOURS_VERIFICATION", 8)
VERIFY_SLUG_TTL_HOURS =  ("VERIFY_SLUG_TTL_HOURS", 48)

SHORTENER_DOMAIN =  ("SHORTENER_DOMAIN", "")
SHORTENER_API =  ("SHORTENER_API_KEY")
CAPTION =  ("CAPTION", "📄{caption}")


# ---------------------------
# Code 2 (Clone Maker Bot) Config
# ---------------------------

CODE2_BOT_TOKEN = os.getenv("CODE2_BOT_TOKEN", "7630512584:AAEAnpDk4dW7Xa9TGEIZ3C37k6CicN7bAnA")
CODE2_API_ID = int(os.getenv("CODE2_API_ID", "15191874"))
CODE2_API_HASH = os.getenv("CODE2_API_HASH", "3037d39233c6fad9b80d83bb8a339a07")
CODE2_MONGO_URI = os.getenv("CODE2_MONGO_URI", "mongodb+srv://hp108044:zWy9AuflXmsrAfSY@cluster0.zlecn7m.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
CODE2_DB_NAME = os.getenv("CODE2_DB_NAME", "clone_maker")

CODE2_ADMINS = list(map(int, os.getenv("CODE2_ADMINS", "5597521952").split(",")))