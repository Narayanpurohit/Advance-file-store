import os

# Fill these values before running
BOT_TOKEN = os.getenv("BOT_TOKEN", "")
API_ID = int(os.getenv("API_ID", "123456"))
API_HASH = os.getenv("API_HASH", "")
MONGO_URI = os.getenv("MONGO_URI", "")

# Admins who can manage the bot
ADMINS = list(map(int, os.getenv("ADMINS", "123456789").split(",")))

# Verification system toggle
VERIFICATION_MODE = os.getenv("VERIFICATION_MODE", "True").lower() == "true"

# Premium settings
PREMIUM_HOURS_VERIFICATION = int(os.getenv("PREMIUM_HOURS_VERIFICATION", "8"))

# Verification slug settings
VERIFY_SLUG_TTL_HOURS = int(os.getenv("VERIFY_SLUG_TTL_HOURS", "48"))  # how long a slug stays valid

# URL shortener service config
SHORTENER_API_KEY = os.getenv("SHORTENER_API_KEY", "")
SHORTENER_API_BASE = os.getenv("SHORTENER_API_BASE", "")

# This will be set automatically at runtime
BOT_USERNAME = None