import json

import httpx
import pytest

from app.features.discovery.deduplication.normalizers import (
    normalize_domain,
    normalize_name,
    normalize_phone,
)
from app.features.discovery.models import GeocodedLocation
from app.features.discovery.providers.base import ProviderError
from app.features.discovery.providers.nominatim import NominatimClient
from app.features.discovery.providers.overpass import OverpassClient, category_tag


def test_normalizers_prepare_strong_deduplication_keys():
    assert normalize_name("The Example Dental, LLC") == "the example dental"
    assert normalize_phone("(512) 555-0198") == "+15125550198"
    assert normalize_domain("https://www.Example.com/contact") == "example.com"
    assert normalize_domain("https://facebook.com/example") is None


@pytest.mark.anyio
async def test_nominatim_client_parses_location_and_identifies_application():
    def handler(request):
        assert request.headers["user-agent"] == "Outrelis-Test/1.0"
        return httpx.Response(200, json=[{
            "display_name": "Austin, Texas, United States", "lat": "30.267153",
            "lon": "-97.743057", "boundingbox": ["30.1", "30.5", "-98", "-97"],
            "osm_type": "relation", "osm_id": 113314, "address": {"country_code": "us"},
        }])
    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as http:
        result = await NominatimClient("https://nominatim.test", "Outrelis-Test/1.0", http).geocode("Austin, TX")
    assert result.osm_area_id == 3600113314
    assert result.normalized_query == "austin tx"
    assert result.bounding_box["west"] == "-98"


@pytest.mark.anyio
async def test_nominatim_reports_unknown_location():
    async with httpx.AsyncClient(transport=httpx.MockTransport(
        lambda _request: httpx.Response(200, json=[]),
    )) as http:
        with pytest.raises(ProviderError, match="No location matched"):
            await NominatimClient("https://nominatim.test", "Outrelis-Test/1.0", http).geocode("Unknown")


@pytest.mark.anyio
async def test_overpass_client_builds_bounded_query_and_parses_businesses():
    def handler(request):
        body = request.content.decode()
        assert '["amenity"="dentist"]' in body
        assert "(30.1,-98,30.5,-97)" in body
        return httpx.Response(200, json={"elements": [{
            "type": "node", "id": 1001, "lat": 30.2, "lon": -97.7,
            "tags": {"name": "Example Dental", "amenity": "dentist", "phone": "512-555-0198",
                     "website": "https://example.test", "addr:city": "Austin", "addr:state": "TX"},
        }]})
    location = GeocodedLocation(
        provider="nominatim", normalized_query="austin tx", display_name="Austin",
        latitude=30.2, longitude=-97.7,
        bounding_box={"south": "30.1", "north": "30.5", "west": "-98", "east": "-97"},
        country_code="us", raw_data={},
    )
    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as http:
        results = await OverpassClient("https://overpass.test/api", "Outrelis-Test/1.0", http).search(
            "Dental clinics", location, 20,
        )
    assert len(results) == 1
    assert results[0].source_id == "1001"
    assert results[0].city == "Austin"


def test_unknown_category_is_rejected_before_network_request():
    with pytest.raises(ProviderError) as error:
        category_tag("Completely unknown industry")
    assert error.value.code == "unsupported_category"
