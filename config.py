
import os
 

BOT_TOKEN =  ("Get from @botfather")
API_ID = ("get from my.telegram.org")
API_HASH =  ("get from my.telegram.org")
MONGO_URI =  ("send mongo db click here to khow how to create :")
DB_NAME =  ("filestore ok")

ADMINS = ("List Admin id like this ")

ENABLE_FSUB = ("click on button to switch value")  
FSUB = ("send channel id list like this ")

VERIFICATION_MODE =  ("")
PREMIUM_HOURS_VERIFICATION = ("how much time.verification from link"))
VERIFY_SLUG_TTL_HOURS = ("")
SHORTENER_DOMAIN = ("url shortner domain name without www or https://")  
SHORTENER_API = ("send shortner api")


CAPTION = "📄file name : {filename}\n💾file size: {filesize}\n\nold caption :{caption}"
# ---------------------------
# Code 2 (Clone Maker Bot) Config
# ---------------------------

CODE2_BOT_TOKEN = os.getenv("CODE2_BOT_TOKEN", "7630512584:AAEAnpDk4dW7Xa9TGEIZ3C37k6CicN7bAnA")
CODE2_API_ID = int(os.getenv("CODE2_API_ID", "15191874"))
CODE2_API_HASH = os.getenv("CODE2_API_HASH", "3037d39233c6fad9b80d83bb8a339a07")
CODE2_MONGO_URI = os.getenv("CODE2_MONGO_URI", "mongodb+srv://hp108044:zWy9AuflXmsrAfSY@cluster0.zlecn7m.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
CODE2_DB_NAME = os.getenv("CODE2_DB_NAME", "clone_maker")

CODE2_ADMINS = list(map(int, os.getenv("CODE2_ADMINS", "5597521952").split(",")))