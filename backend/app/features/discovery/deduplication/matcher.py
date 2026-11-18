from dataclasses import dataclass
from difflib import SequenceMatcher
from math import asin, cos, radians, sin, sqrt

from sqlalchemy.orm import Session

from app.features.discovery import repository
from app.features.discovery.models import Business
from app.features.discovery.providers.base import DiscoveredBusiness
from app.features.discovery.deduplication.normalizers import (
    normalize_domain,
    normalize_name,
    normalize_phone,
    normalize_text,
)


@dataclass(frozen=True)
class BusinessMatch:
    business: Business | None
    reason: str
    confidence: int
    possible_duplicate: bool = False


def distance_meters(first: DiscoveredBusiness, second: Business) -> float | None:
    if None in (first.latitude, first.longitude, second.latitude, second.longitude):
        return None
    lat1, lon1, lat2, lon2 = map(radians, map(float, (
        first.latitude, first.longitude, second.latitude, second.longitude,
    )))
    delta_lat, delta_lon = lat2 - lat1, lon2 - lon1
    value = sin(delta_lat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(delta_lon / 2) ** 2
    return 6371000 * 2 * asin(sqrt(value))


def find_match(db: Session, item: DiscoveredBusiness) -> BusinessMatch:
    source = repository.find_business_by_source(
        db, item.provider, item.source_type, item.source_id,
    )
    if source:
        return BusinessMatch(source[0], "provider_id", 100)
    domain = normalize_domain(item.website_url)
    if domain:
        business = repository.find_business_by_domain(db, domain)
        if business:
            return BusinessMatch(business, "website_domain", 95)
    phone = normalize_phone(item.phone)
    if phone:
        business = repository.find_business_by_phone(db, phone)
        if business:
            return BusinessMatch(business, "phone", 95)

    normalized_name = normalize_name(item.name)
    normalized_address = normalize_text(item.address)
    best: tuple[float, Business] | None = None
    for candidate in repository.find_business_candidates(
        db, item.city, item.region, item.country_code,
    ):
        name_score = SequenceMatcher(None, normalized_name, candidate.normalized_name).ratio()
        address_score = SequenceMatcher(
            None, normalized_address or "", normalize_text(candidate.address) or "",
        ).ratio() if normalized_address and candidate.address else 0
        nearby = distance_meters(item, candidate)
        score = name_score * .7 + address_score * .3
        if nearby is not None and nearby <= 100:
            score += .1
        if best is None or score > best[0]:
            best = (score, candidate)
    if best and best[0] >= .88:
        return BusinessMatch(best[1], "name_address", 90)
    if best and best[0] >= .72:
        return BusinessMatch(best[1], "similar_name_location", 75, True)
    return BusinessMatch(None, "new_business", 100)
