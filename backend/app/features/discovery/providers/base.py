from dataclasses import dataclass, field
from decimal import Decimal
from typing import Protocol

from app.features.discovery.models import GeocodedLocation


class ProviderError(Exception):
    def __init__(self, code: str, detail: str, retryable: bool = False):
        super().__init__(detail)
        self.code = code
        self.detail = detail
        self.retryable = retryable


@dataclass(frozen=True)
class GeocodeResult:
    provider: str
    normalized_query: str
    display_name: str
    latitude: Decimal
    longitude: Decimal
    bounding_box: dict[str, str]
    country_code: str | None
    osm_type: str | None
    osm_id: int | None
    osm_area_id: int | None
    raw_data: dict


@dataclass(frozen=True)
class DiscoveredBusiness:
    provider: str
    source_type: str
    source_id: str
    name: str
    category: str | None = None
    address: str | None = None
    city: str | None = None
    region: str | None = None
    postal_code: str | None = None
    country_code: str | None = None
    phone: str | None = None
    website_url: str | None = None
    latitude: Decimal | None = None
    longitude: Decimal | None = None
    business_status: str = "unknown"
    source_url: str | None = None
    rating: Decimal | None = None
    review_count: int | None = None
    opening_hours: dict | None = None
    raw_data: dict = field(default_factory=dict)


class Geocoder(Protocol):
    async def geocode(self, query: str) -> GeocodeResult: ...


class LeadSource(Protocol):
    async def search(
        self, category: str, location: GeocodedLocation, limit: int,
    ) -> list[DiscoveredBusiness]: ...
