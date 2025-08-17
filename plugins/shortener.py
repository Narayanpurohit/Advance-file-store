import requests
from config import SHORTENER_DOMAIN, SHORTENER_API_KEY

# Map of domain → (mode, API URL format)
SHORTENER_MAP = {
    "shareus.io": ("text", "https://api.shareus.io/easy_api?key={api}&link={url}"),
    "gplinks.in": ("json", "https://api.gplinks.in/st?api={api}&url={url}"),
}


def shorten_url(url: str) -> str:
    """Shorten a URL using the configured shortener."""
    if not SHORTENER_DOMAIN or not SHORTENER_API_KEY:
        return url  # No shortener configured

    try:
        domain = SHORTENER_DOMAIN.lower().replace("www.", "")
        if domain not in SHORTENER_MAP:
            return url

        mode, api_fmt = SHORTENER_MAP[domain]
        api_url = api_fmt.format(api=SHORTENER_API_KEY, url=url)

        resp = requests.get(api_url, timeout=10)
        if resp.status_code != 200:
            return url

        if mode == "text":
            short_url = resp.text.strip()
            if short_url.startswith("http"):
                return short_url

        elif mode == "json":
            data = resp.json()
            if "shortenedUrl" in data:
                return data["shortenedUrl"]

        return url  # fallback

    except Exception as e:
        print(f"[Shortener error] {e}")
        return url