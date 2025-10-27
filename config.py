import os
 

CODE2_BOT_TOKEN = os.getenv("CODE2_BOT_TOKEN", "7630512584:AAGw6bJNlkhnR0RqwCT7BwFk2p18RD8HUMs")
CODE2_API_ID = int(os.getenv("CODE2_API_ID", "15191874"))
CODE2_API_HASH = os.getenv("CODE2_API_HASH", "3037d39233c6fad9b80d83bb8a339a07")
CODE2_MONGO_URI = os.getenv("CODE2_MONGO_URI", "mongodb+srv://hp108044:zWy9AuflXmsrAfSY@cluster0.zlecn7m.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
CODE2_DB_NAME = os.getenv("CODE2_DB_NAME", "clone_maker")
CODE2_LOG_CHANNEL=os.getenv("CODE2_LOG_CHANNEL", "-1002299128264")

CODE2_ADMINS = list(map(int, os.getenv("CODE2_ADMINS", "5597521952").split(",")))