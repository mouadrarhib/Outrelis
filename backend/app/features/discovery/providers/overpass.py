from decimal import Decimal

import httpx

from app.features.discovery.models import GeocodedLocation
from app.features.discovery.providers.base import DiscoveredBusiness, ProviderError

CATEGORY_TAGS = {
    "dental clinic": ("amenity", "dentist"),
    "dental clinics": ("amenity", "dentist"),
    "dentist": ("amenity", "dentist"),
    "dentists": ("amenity", "dentist"),
    "restaurant": ("amenity", "restaurant"),
    "restaurants": ("amenity", "restaurant"),
    "lawyer": ("office", "lawyer"),
    "lawyers": ("office", "lawyer"),
    "accountant": ("office", "accountant"),
    "accountants": ("office", "accountant"),
    "real estate agency": ("office", "estate_agent"),
    "real estate agencies": ("office", "estate_agent"),
}


def category_tag(category: str) -> tuple[str, str]:
    tag = CATEGORY_TAGS.get(" ".join(category.casefold().split()))
    if not tag:
        raise ProviderError(
            "unsupported_category",
            "This business category is not supported by the current data source",
        )
    return tag


def address_from_tags(tags: dict) -> str | None:
    street = " ".join(filter(None, (tags.get("addr:housenumber"), tags.get("addr:street"))))
    parts = [street, tags.get("addr:city"), tags.get("addr:state"), tags.get("addr:postcode")]
    return ", ".join(part for part in parts if part) or None


class OverpassClient:
    def __init__(self, base_url: str, user_agent: str, client: httpx.AsyncClient | None = None):
        self.base_url = base_url.rstrip("/")
        self.user_agent = user_agent
        self.client = client

    async def search(
        self, category: str, location: GeocodedLocation, limit: int,
    ) -> list[DiscoveredBusiness]:
        key, value = category_tag(category)
        box = location.bounding_box
        bbox = ",".join(str(box[name]) for name in ("south", "west", "north", "east"))
        query = (
            f'[out:json][timeout:30];nwr["{key}"="{value}"]({bbox});'
            f"out center tags {limit};"
        )
        try:
            if self.client:
                response = await self.client.post(
                    f"{self.base_url}/interpreter", content=query,
                    headers={"User-Agent": self.user_agent, "Content-Type": "text/plain"},
                )
            else:
                async with httpx.AsyncClient(timeout=45) as client:
                    response = await client.post(
                        f"{self.base_url}/interpreter", content=query,
                        headers={"User-Agent": self.user_agent, "Content-Type": "text/plain"},
                    )
            response.raise_for_status()
        except httpx.HTTPError as error:
            raise ProviderError("lead_source_unavailable", "Business search is unavailable", True) from error
        results = []
        for element in response.json().get("elements", []):
            tags = element.get("tags") or {}
            name = tags.get("name")
            if not name:
                continue
            center = element.get("center") or element
            lat, lon = center.get("lat"), center.get("lon")
            results.append(DiscoveredBusiness(
                provider="openstreetmap",
                source_type=element["type"],
                source_id=str(element["id"]),
                name=name,
                category=tags.get("name:en") or tags.get(key) or value,
                address=address_from_tags(tags),
                city=tags.get("addr:city"),
                region=tags.get("addr:state"),
                postal_code=tags.get("addr:postcode"),
                country_code=(tags.get("addr:country") or location.country_code),
                phone=tags.get("contact:phone") or tags.get("phone"),
                website_url=tags.get("contact:website") or tags.get("website"),
                latitude=Decimal(str(lat)) if lat is not None else None,
                longitude=Decimal(str(lon)) if lon is not None else None,
                business_status="active" if not tags.get("disused") else "closed",
                source_url=f"https://www.openstreetmap.org/{element['type']}/{element['id']}",
                opening_hours={"raw": tags["opening_hours"]} if tags.get("opening_hours") else None,
                raw_data=element,
            ))
        return results[:limit]
