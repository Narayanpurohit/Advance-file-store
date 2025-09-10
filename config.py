
import os
 

HELP_TEXTS = {
    "BOT_TOKEN": "Get from @botfather",
    "API_ID": "Get from my.telegram.org",
    "API_HASH": "Get from my.telegram.org",
    "MONGO_URI": "Send Mongo DB URI. Click here to know how to create.",
    "DB_NAME": "Your Mongo DB database name",
    "ADMINS": "List of admin user IDs separated by spaces",
    "ENABLE_FSUB": "Click the button to toggle True/False",
    "FSUB": "Channel ID list separated by spaces",
    "VERIFICATION_MODE": "Set True or False for verification mode",
    "PREMIUM_HOURS_VERIFICATION": "How many hours verification is valid",
    "VERIFY_SLUG_TTL_HOURS": "Slug validity duration in hours",
    "SHORTENER_DOMAIN": "Your URL shortener domain (without www or https://)",
    "SHORTENER_API_KEY": "API key for your URL shortener service",
    "CAPTION": "File caption template, e.g., 📄 Name: {filename}\n💾 Size: {filesize}",
    "PREMIUM_POINTS": "How many points to give for premium",
    "LOG_CHANNEL_ID": "Log channel ID for bot logs"
}
# ---------------------------
# Code 2 (Clone Maker Bot) Config
# ---------------------------

CODE2_BOT_TOKEN = os.getenv("CODE2_BOT_TOKEN", "7630512584:AAEAnpDk4dW7Xa9TGEIZ3C37k6CicN7bAnA")
CODE2_API_ID = int(os.getenv("CODE2_API_ID", "15191874"))
CODE2_API_HASH = os.getenv("CODE2_API_HASH", "3037d39233c6fad9b80d83bb8a339a07")
CODE2_MONGO_URI = os.getenv("CODE2_MONGO_URI", "mongodb+srv://hp108044:zWy9AuflXmsrAfSY@cluster0.zlecn7m.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
CODE2_DB_NAME = os.getenv("CODE2_DB_NAME", "clone_maker")

CODE2_ADMINS = list(map(int, os.getenv("CODE2_ADMINS", "5597521952").split(",")))