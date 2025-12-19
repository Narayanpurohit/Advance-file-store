import requests
import logging
from bot import get_str

log = logging.getLogger(__name__)

# ===================== SUPPORTED SHORTENERS =====================
SHORTENER_MAP = {
    "shareus.io": lambda api, url: f"https://api.shareus.io/easy_api?key={api}&link={url}",
    "gplinks.com": lambda api, url: f"https://api.gplinks.com/api?api={api}&url={url}&format=json",
    "linkshortify.com": lambda api, url: f"https://linkshortify.com/st?api={api}&url={url}",
}


def _call_shortener(api_url: str):
    """Internal helper to call shortener API safely"""
    try:
        resp = requests.get(api_url, timeout=10)
        resp.raise_for_status()

        # Try JSON response
        try:
            data = resp.json()
            if isinstance(data, dict):
                for key in ("shortenedUrl", "short_url", "short"):
                    if key in data and str(data[key]).startswith("http"):
                        return data[key]
        except ValueError:
            pass

        # Plain text fallback
        text = resp.text.strip()
        if text.startswith("http"):
            return text

        return None

    except Exception as e:
        log.warning(f"⚠️ Shortener request failed: {e}")
        return None


def shorten_url(url: str):
    """
    Shorten URL with smart fallback:
    1️⃣ Try configured SHORTENER_DOMAIN first
    2️⃣ If not mapped or fails → try all supported shorteners
    """

    domain = get_str("SHORTENER_DOMAIN").lower().strip()
    api_key = get_str("SHORTENER_API_KEY").strip()

    if not api_key:
        log.warning("⚠️ Shortener API key not configured.")
        return None, "Shortener not configured"

    tried = []

    # -------- 1️⃣ Try configured domain first --------
    if domain and domain in SHORTENER_MAP:
        builder = SHORTENER_MAP[domain]
        api_url = builder(api_key, url)

        log.info(f"🔍 Trying mapped shortener [{domain}]")
        short = _call_shortener(api_url)

        if short:
            log.info(f"✅ Shortened via {domain}: {short}")
            return short, None

        tried.append(domain)

    # -------- 2️⃣ Fallback: try all shorteners --------
    for name, builder in SHORTENER_MAP.items():
        if name in tried:
            continue

        api_url = builder(api_key, url)
        log.info(f"🔁 Trying fallback shortener [{name}]")

        short = _call_shortener(api_url)
        if short:
            log.info(f"✅ Shortened via {name}: {short}")
            return short, None

    # -------- 3️⃣ Total failure --------
    log.error("❌ All shorteners failed")
    return None, "Unable to shorten URL with any provider"