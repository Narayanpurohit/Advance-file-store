# Create verification slug linked to user_id
def create_verification_slug(user_id: int, ttl_hours: int):
    slug = "verify_" + "".join(random.choices(string.ascii_letters + string.digits, k=30))
    expires_at = datetime.datetime.utcnow() + datetime.timedelta(hours=ttl_hours)
    verify_col.insert_one({
        "slug": slug,
        "user_id": user_id,
        "expires_at": expires_at
    })
    return slug


# Use verification slug (return doc if valid)
def use_verification_slug(slug: str):
    doc = verify_col.find_one({"slug": slug})
    if not doc:
        return None
    if datetime.datetime.utcnow() > doc["expires_at"]:
        verify_col.delete_one({"slug": slug})
        return None
    verify_col.delete_one({"slug": slug})  # Remove after use
    return doc