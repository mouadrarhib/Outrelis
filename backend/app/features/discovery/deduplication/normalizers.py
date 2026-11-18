import re
import unicodedata
from urllib.parse import urlsplit


def normalize_text(value: str | None) -> str | None:
    if not value:
        return None
    ascii_value = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode()
    normalized = re.sub(r"[^a-z0-9]+", " ", ascii_value.casefold()).strip()
    return re.sub(r"\s+", " ", normalized) or None


def normalize_name(value: str) -> str:
    normalized = normalize_text(value) or ""
    suffixes = {"llc", "inc", "ltd", "corp", "corporation", "company", "co"}
    words = normalized.split()
    while words and words[-1] in suffixes:
        words.pop()
    return " ".join(words) or normalized


def normalize_phone(value: str | None) -> str | None:
    if not value:
        return None
    digits = re.sub(r"\D", "", value)
    if len(digits) == 10:
        digits = "1" + digits
    return "+" + digits if 8 <= len(digits) <= 15 else None


def normalize_domain(value: str | None) -> str | None:
    if not value:
        return None
    candidate = value if "://" in value else "https://" + value
    hostname = (urlsplit(candidate).hostname or "").casefold().rstrip(".")
    if hostname.startswith("www."):
        hostname = hostname[4:]
    blocked = {"facebook.com", "instagram.com", "linkedin.com", "linktr.ee", "yelp.com"}
    return None if not hostname or hostname in blocked else hostname
