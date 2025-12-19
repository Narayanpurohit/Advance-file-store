import requests
import logging
from bot import get_str

log = logging.getLogger(__name__)

# ===================== SUPPORTED SHORTENERS =====================
SHORTENER_MAP = {
    "shareus.io": lambda api, url: f"https://api.shareus.io/easy_api?key={api}&link={url}",
    "gplinks.com": lambda api, url: f"https://api.gplinks.com/api?api={api}&url={url}&format=json",
    "linkshortify.com": lambda api, url: f"https://linkshortify.com/api?api={api}&url={url}",
}


def shorten_url(url: str):
    """
    Dynamically shorten a URL using configured shortener.
    Fetches SHORTENER_DOMAIN and SHORTENER_API_KEY from DB each time.
    Returns: (short_link or None, error_message or None)
    """
    domain = get_str("SHORTENER_DOMAIN").lower().strip()
    api_key = get_str("SHORTENER_API_KEY").strip()

    if not domain or not api_key:
        log.warning("⚠️ Shortener not configured.")
        return None, "Shortener not configured"

    builder = SHORTENER_MAP.get(domain)
    if not builder:
        log.error(f"❌ Unsupported shortener domain: {domain}")
        return None, f"No mapping for shortener domain '{domain}'"

    api_url = builder(api_key, url)
    log.info(f"🔗 Requesting shortener: {api_url}")

    try:
        resp = requests.get(api_url, timeout=10)
        resp.raise_for_status()

        # Try to parse JSON response
        try:
            data = resp.json()
            if "shortenedUrl" in data:
                short_url = data["shortenedUrl"]
                log.info(f"✅ Shortened URL (JSON): {short_url}")
                return short_url, None
        except ValueError:
            pass  # Not JSON

        # Fallback to plain text response
        text = resp.text.strip()
        if text.startswith("http"):
            log.info(f"✅ Shortened URL (Text): {text}")
            return text, None

        log.error(f"⚠️ Unexpected shortener response: {resp.text[:100]}")
        return None, f"Unexpected response: {resp.text[:100]}"

    except Exception as e:
        log.error(f"❌ Shortener failed: {e}")
        return None, str(e)