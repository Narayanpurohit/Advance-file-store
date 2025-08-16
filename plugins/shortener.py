import requests
from config import SHORTENER_DOMAIN, SHORTENER_API_KEY

# Mapping dictionary: domain → API URL pattern
SHORTENER_FORMATS = {
    "shareus.io": "https://api.shareus.io/easy_api?key={api}&link={url}",
    "gplinks.in": "https://api.gplinks.com/st?api={api}&url={url}",
}

def shorten_url(long_url: str) -> str:
    """Shorten a URL using the configured shortener domain & API key."""
    if not SHORTENER_DOMAIN or not SHORTENER_API_KEY:
        return long_url  # No shortener configured

    # Match domain to format
    api_format = SHORTENER_FORMATS.get(SHORTENER_DOMAIN.lower())
    if not api_format:
        return long_url  # Unsupported shortener

    try:
        # Build the request URL
        api_url = api_format.format(api=SHORTENER_API_KEY, url=long_url)

        # Call the shortener API
        resp = requests.get(api_url, timeout=10)
        data = resp.json()

        # Handle known response fields
        if "shortenedUrl" in data:
            return data["shortenedUrl"]
        if "shortenUrl" in data:
            return data["shortenUrl"]
        if "short" in data:
            return data["short"]

        # Fallback: try first value in response
        return next(iter(data.values())) if isinstance(data, dict) else long_url

    except Exception as e:
        print(f"[Shortener error] {e}")
        return long_url