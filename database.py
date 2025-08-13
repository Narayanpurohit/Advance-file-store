from pymongo import MongoClient
from config import MONGO_URI
import datetime

client = MongoClient(MONGO_URI)
db = client["fileshare_bot"]

users_col = db["users"]
files_col = db["files"]
stats_col = db["stats"]
premium_col = db["premium"]
verify_col = db["verify"]

def add_user(user_id):
    if not users_col.find_one({"_id": user_id}):
        users_col.insert_one({"_id": user_id})
        stats_col.update_one({"_id": "stats"}, {"$inc": {"total_users": 1}}, upsert=True)

def is_premium(user_id):
    record = premium_col.find_one({"_id": user_id})
    if not record:
        return False
    return record["expiry"] > datetime.datetime.utcnow()

def add_premium(user_id, hours):
    expiry = datetime.datetime.utcnow() + datetime.timedelta(hours=hours)
    premium_col.update_one({"_id": user_id}, {"$set": {"expiry": expiry}}, upsert=True)

def remove_premium(user_id):
    premium_col.delete_one({"_id": user_id})

def add_file(slug, file_id, file_type):
    files_col.insert_one({"_id": slug, "file_id": file_id, "type": file_type})

def get_file(slug):
    return files_col.find_one({"_id": slug})

def inc_sent_count():
    stats_col.update_one({"_id": "stats"}, {"$inc": {"files_sent": 1}}, upsert=True)

def get_stats():
    data = stats_col.find_one({"_id": "stats"}) or {}
    return data.get("total_users", 0), data.get("files_sent", 0)

def create_verification(slug, user_id):
    verify_col.insert_one({"_id": slug, "user_id": user_id, "created": datetime.datetime.utcnow()})

def get_verification(slug):
    return verify_col.find_one({"_id": slug})

def delete_verification(slug):
    verify_col.delete_one({"_id": slug})