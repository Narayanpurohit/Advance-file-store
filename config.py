import os
from dotenv import load_dotenv
load_dotenv()

# Telegram
BOT_TOKEN = os.getenv("BOT_TOKEN", "YOUR_BOT_TOKEN")
API_ID = int(os.getenv("API_ID", "123456"))
API_HASH = os.getenv("API_HASH", "YOUR_API_HASH")

# Private storage channel (must start with -100...)
STORAGE_CHANNEL = int(os.getenv("STORAGE_CHANNEL", "-1001234567890"))

# Admin user IDs (comma-separated in env)
ADMINS = [int(x) for x in os.getenv("ADMINS", "123456789").split(",") if x.strip()]

# MongoDB
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
DB_NAME = os.getenv("DB_NAME", "file_store_bot")

# Verification / Premium
VERIFY_PREMIUM_HOURS = int(os.getenv("VERIFY_PREMIUM_HOURS", "8"))  # premium time granted after verification
VERIFY_SLUG_RANDOM_LEN = 30  # random part length AFTER the 'verify_' prefix
VERIFY_SLUG_TTL_HOURS = int(os.getenv("VERIFY_SLUG_TTL_HOURS", "48"))  # how long a slug stays valid

# URL shortener (plug your service here)
SHORTENER_API_KEY = os.getenv("SHORTENER_API_KEY", "")
SHORTENER_API_BASE = os.getenv("SHORTENER_API_BASE", "")  # e.g. https://api.shrinkme.io/api
SHORTENER_DOMAIN = os.getenv("SHORTENER_DOMAIN", "https://t.me")  # fallback if not shortening

# If True, send file directly to premium users; non-premium must verify
PREMIUM_BYPASS = True