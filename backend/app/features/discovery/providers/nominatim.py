import asyncio
from decimal import Decimal
from time import monotonic

import httpx

from app.features.discovery.deduplication.normalizers import normalize_text
from app.features.discovery.providers.base import GeocodeResult, ProviderError


class NominatimClient:
    def __init__(
        self, base_url: str, user_agent: str, client: httpx.AsyncClient | None = None,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.user_agent = user_agent
        self.client = client
        self._lock = asyncio.Lock()
        self._last_request = 0.0

    async def geocode(self, query: str) -> GeocodeResult:
        async with self._lock:
            wait = 1.0 - (monotonic() - self._last_request)
            if wait > 0:
                await asyncio.sleep(wait)
            try:
                if self.client:
                    response = await self.client.get(
                        f"{self.base_url}/search",
                        params={"q": query, "format": "jsonv2", "limit": 1, "addressdetails": 1},
                        headers={"User-Agent": self.user_agent},
                    )
                else:
                    async with httpx.AsyncClient(timeout=20) as client:
                        response = await client.get(
                            f"{self.base_url}/search",
                            params={"q": query, "format": "jsonv2", "limit": 1, "addressdetails": 1},
                            headers={"User-Agent": self.user_agent},
                        )
                self._last_request = monotonic()
                response.raise_for_status()
            except httpx.HTTPError as error:
                raise ProviderError("geocoding_unavailable", "Location lookup is unavailable", True) from error
        data = response.json()
        if not data:
            raise ProviderError("location_not_found", f"No location matched {query}")
        item = data[0]
        box = item.get("boundingbox") or []
        if len(box) != 4:
            raise ProviderError("invalid_geocoding_response", "Location bounds were unavailable")
        osm_type = item.get("osm_type")
        osm_id = int(item["osm_id"]) if item.get("osm_id") is not None else None
        area_offset = {"relation": 3_600_000_000, "way": 2_400_000_000}.get(osm_type)
        return GeocodeResult(
            provider="nominatim",
            normalized_query=normalize_text(query) or query.casefold(),
            display_name=item["display_name"],
            latitude=Decimal(item["lat"]),
            longitude=Decimal(item["lon"]),
            bounding_box={"south": box[0], "north": box[1], "west": box[2], "east": box[3]},
            country_code=(item.get("address") or {}).get("country_code"),
            osm_type=osm_type,
            osm_id=osm_id,
            osm_area_id=osm_id + area_offset if osm_id is not None and area_offset else None,
            raw_data=item,
        )
