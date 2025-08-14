import time
from typing import Optional, Dict, Any
from pymongo import MongoClient
from config import MONGO_URI

# ───────────────── Mongo Connection (fixed DB name) ─────────────────
_client = MongoClient(MONGO_URI)
_db = _client["filestore"]

# Expose raw collections (some plugins import these directly)
users_col = _db["users"]
files_col = _db["files"]
stats_col = _db["stats"]
verify_col = _db["verify"]  # verification links


class DB:
    """Helper with all DB operations used across plugins."""

    def __init__(self):
        self.users = users_col
        self.files = files_col
        self.stats = stats_col
        self.verify = verify_col

    # ─────────────── Users / Premium ───────────────
    def user_exists(self, user_id: int) -> bool:
        return self.users.find_one({"user_id": user_id}) is not None

    def add_user(self, user_id: int) -> None:
        if not self.user_exists(user_id):
            self.users.insert_one({
                "user_id": user_id,
                "is_premium": False,
                "premium_expiry": None
            })

    def is_premium(self, user_id: int) -> bool:
        """Checks premium and auto-expires if past expiry."""
        user = self.users.find_one({"user_id": user_id})
        if not user:
            return False
        expiry = user.get("premium_expiry")
        if expiry and time.time() > float(expiry):
            # Premium expired → flip flag off
            self.users.update_one(
                {"user_id": user_id},
                {"$set": {"is_premium": False, "premium_expiry": None}}
            )
            return False
        return bool(user.get("is_premium", False))

    def upgrade_to_premium(self, user_id: int, hours: int) -> float:
        """Give premium for N hours. Returns expiry timestamp."""
        expiry_time = time.time() + (int(hours) * 3600)
        self.users.update_one(
            {"user_id": user_id},
            {"$set": {"is_premium": True, "premium_expiry": expiry_time}},
            upsert=True
        )
        return expiry_time

    def add_premium(self, user_id: int, days: int) -> float:
        """Give premium for N days. Returns expiry timestamp."""
        return self.upgrade_to_premium(user_id, hours=int(days) * 24)

    def remove_premium(self, user_id: int) -> None:
        self.users.update_one(
            {"user_id": user_id},
            {"$set": {"is_premium": False, "premium_expiry": None}},
            upsert=True
        )

    # ─────────────── Files ───────────────
    def save_file_record(
        self,
        slug: str,
        file_id: str,
        file_type: str,
        file_name: Optional[str],
        file_size: Optional[int],
        caption: Optional[str]
    ) -> None:
        self.files.insert_one({
            "slug": slug,
            "file_id": file_id,
            "file_type": file_type,      # "doc" | "vid" | "aud"
            "file_name": file_name or "",
            "file_size": int(file_size or 0),
            "caption": caption or ""
        })

    def get_file_by_slug(self, slug: str) -> Optional[Dict[str, Any]]:
        return self.files.find_one({"slug": slug})

    # ─────────────── Stats ───────────────
    def increment_file_send_count(self, n: int = 1) -> None:
        """Total number of files served to users."""
        self.stats.update_one(
            {"_id": "total"},
            {"$inc": {"sent_files": int(n)}},
            upsert=True
        )

    def get_file_send_count(self) -> int:
        doc = self.stats.find_one({"_id": "total"}) or {}
        return int(doc.get("sent_files", 0))

    # ─────────────── Verification Links ───────────────
    def save_verification_slug(self, user_id: int, slug: str, expiry_hours: int) -> float:
        """Create/overwrite a verify slug for a user. Returns expires_at timestamp."""
        now = time.time()
        expires_at = now + (int(expiry_hours) * 3600)
        # One slug per document (unique by slug)
        self.verify.update_one(
            {"slug": slug},
            {"$set": {
                "slug": slug,
                "user_id": user_id,
                "created_at": now,
                "expires_at": expires_at
            }},
            upsert=True
        )
        return expires_at

    def is_verification_valid(self, user_id: int, slug: str) -> bool:
        """True if slug exists, belongs to user, and not expired."""
        rec = self.verify.find_one({"slug": slug})
        if not rec:
            return False
        if rec.get("user_id") != user_id:
            return False
        exp = rec.get("expires_at")
        if not exp or time.time() > float(exp):
            # Clean expired record
            self.verify.delete_one({"slug": slug})
            return False
        return True

    def remove_verification_slug(self, user_id: int, slug: str) -> None:
        self.verify.delete_one({"slug": slug, "user_id": user_id})
    


# Instantiate a helper so `from database import db` works
db = DB()

# ─────────────── Optional module-level wrappers ───────────────
# These let older plugins do `from database import add_premium, is_premium, ...`
def user_exists(user_id: int) -> bool: return db.user_exists(user_id)
def add_user(user_id: int) -> None: return db.add_user(user_id)
def is_premium(user_id: int) -> bool: return db.is_premium(user_id)
def add_premium(user_id: int, days: int) -> float: return db.add_premium(user_id, days)
def remove_premium(user_id: int) -> None: return db.remove_premium(user_id)
def save_file_record(slug: str, file_id: str, file_type: str, file_name: Optional[str], file_size: Optional[int], caption: Optional[str]) -> None:
    return db.save_file_record(slug, file_id, file_type, file_name, file_size, caption)
def get_file_by_slug(slug: str) -> Optional[Dict[str, Any]]: return db.get_file_by_slug(slug)
def increment_file_send_count(n: int = 1) -> None: return db.increment_file_send_count(n)
def get_file_send_count() -> int: return db.get_file_send_count()
def save_verification_slug(user_id: int, slug: str, expiry_hours: int) -> float: return db.save_verification_slug(user_id, slug, expiry_hours)
def is_verification_valid(user_id: int, slug: str) -> bool: return db.is_verification_valid(user_id, slug)
def remove_verification_slug(user_id: int, slug: str) -> None: return db.remove_verification_slug(user_id, slug)
    def get_stats():
    """Backward compatibility: return a dict with current stats."""
    return {
        "sent_files": get_file_send_count(),
        "total_users": users_col.count_documents({}),
        "total_files": files_col.count_documents({})
    }