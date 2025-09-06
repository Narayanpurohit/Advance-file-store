# db_config.py

from pymongo import MongoClient
from config import CODE2_MONGO_URI, CODE2_DB_NAME   # ✅ import from config.py

# ---------------- MONGO CONNECTION ----------------
mongo_client = MongoClient(CODE2_MONGO_URI)
db = mongo_client[CODE2_DB_NAME]

# ✅ Collections
users_col = db["users"]