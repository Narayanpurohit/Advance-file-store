import os

# Fill these values before running
BOT_TOKEN = os.getenv("BOT_TOKEN", "6677023637:AAEzYMmsN_aqsIUtMl8D8hgId74z6hUJa0Q")
API_ID = int(os.getenv("API_ID", "15191874"))
API_HASH = os.getenv("API_HASH", "3037d39233c6fad9b80d83bb8a339a07")
MONGO_URI = os.getenv("MONGO_URI", "mongodb+srv://hp108044:zWy9AuflXmsrAfSY@cluster0.zlecn7m.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")

# Admins who can manage the bot
ADMINS = list(map(int, os.getenv("ADMINS", "5597521952").split(",")))

# Verification system toggle
VERIFICATION_MODE = os.getenv("VERIFICATION_MODE", "True").lower() == "true"

# Premium settings
PREMIUM_HOURS_VERIFICATION = int(os.getenv("PREMIUM_HOURS_VERIFICATION", "8"))

# Verification slug settings
VERIFY_SLUG_TTL_HOURS = int(os.getenv("VERIFY_SLUG_TTL_HOURS", "48"))  # how long a slug stays valid

# URL shortener service config

SHORTENER_DOMAIN = "gplinks.in"   # or "gplinks.in"
SHORTENER_API_KEY = "4aac6a311c58f4d5a739dd10c22d65db725e2988"


SHORTENER_API_KEY = "zu1xmKAMdlguQSBt5c8ais2aV212"
SHORTENER_API_BASE = "https://api.shareus.io/easy_api"
# This will be set automatically at runtime
BOT_USERNAME = None
CAPTION = "📄 **{filename}**\n💾 {filesize}\n\n{caption}"