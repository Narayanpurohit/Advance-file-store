import requests
from urllib.parse import urlparse
from config import SHORTENER_API_KEY, SHORTENER_DOMAIN

# Mapping of shortener domains -> (response_type, api_format)
SHORTENER_MAP = {
    "shareus.io": ("json", "https://api.shareus.io/easy_api?key={api}&link={url}"),
    "gplinks.com": ("json", "https://api.gplinks.com/st?api={api}&url={url}"),
    # Add more mappings here if needed
}


def normalize_domain(domain: str) -> str:
    """Normalize domain to a standard form for matching."""
    domain = domain.lower().strip()
    if domain.startswith("www."):
        domain = domain[4:]
    # handle gplinks.in -> gplinks.com
    if domain in ["gplinks.in", "www.gplinks.in"]:
        domain = "gplinks.com"
    return domain


def shorten_url(url: str) -> str:
    """Shorten URL using selected shortener service."""
    if not SHORTENER_DOMAIN or not SHORTENER_API_KEY:
        return url

    domain = normalize_domain(SHORTENER_DOMAIN)
    if domain not in SHORTENER_MAP:
        print(f"[Shortener error] No mapping for domain {domain}")
        return url

    resp_type, api_format = SHORTENER_MAP[domain]
    api_url = api_format.format(api=SHORTENER_API_KEY, url=url)

    try:
        resp = requests.get(api_url, timeout=10)
        resp.raise_for_status()

        if resp_type == "json":
            data = resp.json()
            # Both Shareus and GPlinks use `shortenedUrl`
            return data.get("shortenedUrl") or url
        else:
            return resp.text.strip() or url
    except Exception as e:
        print(f"[Shortener error] {e}")
        return url