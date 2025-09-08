import requests
from bot import SHORTENER_DOMAIN, SHORTENER_API

# Map of supported shorteners and their API formats
SHORTENER_MAP = {
    "shareus.io": lambda api, url: f"https://api.shareus.io/easy_api?key={api}&link={url}",
    "gplinks.com": lambda api, url: f"https://api.gplinks.com/api?api={api}&url={url}&format=json",
}


def shorten_url(url: str) -> str:
    domain = SHORTENER_DOMAIN.lower().strip() if SHORTENER_DOMAIN else None
    api_key = SHORTENER_API.strip() if SHORTENER_API else None

    if not domain or not api_key:
        return url  # No shortener configured

    builder = SHORTENER_MAP.get(domain)
    if not builder:
        print(f"[Shortener] No mapping for domain {domain}, returning original link")
        return url

    api_url = builder(api_key, url)

    try:
        resp = requests.get(api_url, timeout=10)
        resp.raise_for_status()

        # Handle JSON responses
        try:
            data = resp.json()
            if "shortenedUrl" in data:
                return data["shortenedUrl"]
        except ValueError:
            pass  # Not JSON, maybe plain text

        # Handle plain text
        text = resp.text.strip()
        if text.startswith("http"):
            return text

    except Exception as e:
        print(f"[Shortener error] {e}")

    return url  # fallback to original link