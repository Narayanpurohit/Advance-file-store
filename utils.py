# utils.py
def human_readable_size(size_bytes: int) -> str:
    """
    Convert bytes to a human-readable format (KB, MB, GB, etc.)
    """
    if size_bytes == 0:
        return "0B"

    size_name = ("B", "KB", "MB", "GB", "TB", "PB")
    i = 0
    double_size = float(size_bytes)
    while double_size >= 1024 and i < len(size_name) - 1:
        double_size /= 1024
        i += 1
    return f"{double_size:.2f} {size_name[i]}"