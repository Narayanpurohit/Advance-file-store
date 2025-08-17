import requests
from config import SHORTENER_DOMAIN, SHORTENER_API_KEY

# Map each shortener domain to its API format
SHORTENER_MAP = {
    "shareus.io": lambda api, link: f"https://api.shareus.io/easy_api?key={api}&link={link}",
    "gplinks.com": lambda api, link: f"https://api.gplinks.com/st?api={api}&url={link}",
    # You can add more mappings here later
}

def shorten_url(url: str) -> str:
    """Shorten a URL using the configured shortener domain + API key."""
    if not SHORTENER_DOMAIN or not SHORTENER_API_KEY:
        return url

    try:
        domain = SHORTENER_DOMAIN.lower().replace("www.", "")
        if domain in SHORTENER_MAP:
            api_url = SHORTENER_MAP[domain](SHORTENER_API_KEY, url)
            resp = requests.get(api_url, timeout=10)

            # Shareus & GPlink return plain text (shortened URL), not JSON
            if resp.status_code == 200:
                short_url = resp.text.strip()
                if short_url.startswith("http"):
                    return short_url

        # fallback if something failed
        return url

    except Exception as e:
        print(f"[Shortener error] {e}")
        return url