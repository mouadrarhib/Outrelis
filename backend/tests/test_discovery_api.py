from decimal import Decimal
from uuid import UUID

import pytest
from sqlalchemy import func, select

from app.features.discovery.models import (
    Business,
    BusinessSource,
    GeocodedLocation,
    SearchJob,
    SearchJobLead,
    SearchJobLocation,
)
from app.features.discovery.providers.base import (
    DiscoveredBusiness,
    GeocodeResult,
    ProviderError,
)
from app.features.discovery.worker import process_job

PASSWORD = "a long private passphrase"


def register_setup(client, email="search@example.com", locations=None):
    locations = locations or ["Austin, TX"]
    registration = client.post("/api/v1/auth/register", json={
        "full_name": "Search Owner", "email": email, "password": PASSWORD,
    })
    login = client.post("/api/v1/auth/login", json={"email": email, "password": PASSWORD})
    token = login.json()["access_token"]
    setup = client.put("/api/v1/prospecting/setup", headers={
        "Authorization": f"Bearer {token}",
    }, json={
        "service_name": "Website design",
        "outreach_language": "en-US",
        "business_category": "Dental clinics",
        "locations": locations,
        "result_limit_per_location": 20,
    })
    return registration.json(), token, setup.json()["search_draft"]["id"]


def auth(token):
    return {"Authorization": f"Bearer {token}"}


def create_job(client, token, draft_id):
    return client.post(
        "/api/v1/search-jobs", headers=auth(token), json={"search_draft_id": draft_id},
    )


class FakeGeocoder:
    def __init__(self):
        self.calls = []

    async def geocode(self, query):
        self.calls.append(query)
        slug = query.casefold().replace(",", "")
        return GeocodeResult(
            provider="nominatim",
            normalized_query=slug,
            display_name=f"{query}, United States",
            latitude=Decimal("30.267153"),
            longitude=Decimal("-97.743057"),
            bounding_box={"south": "30.1", "north": "30.5", "west": "-98", "east": "-97"},
            country_code="us",
            osm_type="relation",
            osm_id=113314,
            osm_area_id=3600113314,
            raw_data={"query": query},
        )


class FakeLeadSource:
    def __init__(self, fail_query=None):
        self.fail_query = fail_query
        self.calls = []

    async def search(self, category, location, limit):
        self.calls.append((category, location.normalized_query, limit))
        if self.fail_query and self.fail_query in location.normalized_query:
            raise ProviderError("lead_source_unavailable", "Business search is unavailable", True)
        return [
            DiscoveredBusiness(
                provider="openstreetmap", source_type="node", source_id="1001",
                name="Example Dental LLC", category="dentist",
                address="100 Main St, Austin, TX", city="Austin", region="TX",
                country_code="us", phone="(512) 555-0198",
                website_url="https://www.example-dental.test/contact",
                latitude=Decimal("30.267200"), longitude=Decimal("-97.743100"),
                source_url="https://www.openstreetmap.org/node/1001",
                raw_data={"type": "node", "id": 1001},
            ),
            DiscoveredBusiness(
                provider="openstreetmap", source_type="way", source_id="2002",
                name="Example Dental", category="dentist", city="Austin", region="TX",
                country_code="us", phone="+1 512 555 0198",
                website_url="https://example-dental.test",
                latitude=Decimal("30.267201"), longitude=Decimal("-97.743101"),
                raw_data={"type": "way", "id": 2002},
            ),
        ]


def test_search_job_endpoints_require_authentication(client):
    assert client.post("/api/v1/search-jobs", json={"search_draft_id": "00000000-0000-0000-0000-000000000000"}).status_code == 401
    assert client.get("/api/v1/search-jobs/00000000-0000-0000-0000-000000000000").status_code == 401


def test_create_job_snapshots_setup_and_locations(client, db):
    user, token, draft_id = register_setup(client, locations=["Austin, TX", "Dallas, TX"])

    response = create_job(client, token, draft_id)

    assert response.status_code == 201
    assert response.headers["cache-control"] == "no-store"
    body = response.json()
    assert body["status"] == "queued"
    assert body["category"] == "Dental clinics"
    assert body["total_locations"] == 2
    assert [item["location_query"] for item in body["locations"]] == ["Austin, TX", "Dallas, TX"]
    assert str(db.scalar(select(SearchJob)).user_id) == user["id"]


def test_user_can_only_have_one_active_job(client):
    _, token, draft_id = register_setup(client)
    assert create_job(client, token, draft_id).status_code == 201

    response = create_job(client, token, draft_id)

    assert response.status_code == 409
    assert response.json()["code"] == "active_search_exists"


def test_jobs_are_isolated_by_user(client):
    _, first_token, first_draft = register_setup(client, "first-job@example.com")
    _, second_token, _ = register_setup(client, "second-job@example.com")
    job_id = create_job(client, first_token, first_draft).json()["id"]

    assert client.get(f"/api/v1/search-jobs/{job_id}", headers=auth(second_token)).status_code == 404
    assert client.get(f"/api/v1/search-jobs/{job_id}/leads", headers=auth(second_token)).status_code == 404


@pytest.mark.anyio
async def test_worker_deduplicates_by_domain_and_phone_and_completes_job(client, db):
    _, token, draft_id = register_setup(client, locations=["Austin, TX", "Dallas, TX"])
    job_id = UUID(create_job(client, token, draft_id).json()["id"])
    job = db.get(SearchJob, job_id)
    geocoder, source = FakeGeocoder(), FakeLeadSource()

    await process_job(db, job, geocoder, source)
    db.expire_all()
    saved = db.get(SearchJob, job_id)

    assert saved.status == "completed"
    assert saved.processed_locations == 2
    assert saved.businesses_found == 1
    assert db.scalar(select(func.count()).select_from(Business)) == 1
    assert db.scalar(select(func.count()).select_from(BusinessSource)) == 2
    assert db.scalar(select(func.count()).select_from(SearchJobLead)) == 1
    assert len(geocoder.calls) == 2
    assert len(source.calls) == 2

    leads = client.get(f"/api/v1/search-jobs/{job_id}/leads", headers=auth(token))
    assert leads.status_code == 200
    assert leads.json()["total"] == 1
    assert leads.json()["items"][0]["name"] == "Example Dental LLC"


@pytest.mark.anyio
async def test_worker_uses_cached_geocoding_result(client, db):
    _, token, draft_id = register_setup(client)
    job_id = UUID(create_job(client, token, draft_id).json()["id"])
    db.add(GeocodedLocation(
        provider="nominatim", normalized_query="austin tx", display_name="Austin, Texas",
        latitude=Decimal("30.267153"), longitude=Decimal("-97.743057"),
        bounding_box={"south": "30.1", "north": "30.5", "west": "-98", "east": "-97"},
        country_code="us", raw_data={},
    ))
    db.commit()
    geocoder, source = FakeGeocoder(), FakeLeadSource()

    await process_job(db, db.get(SearchJob, job_id), geocoder, source)

    assert geocoder.calls == []
    assert len(source.calls) == 1


@pytest.mark.anyio
async def test_worker_marks_a_partial_result_when_one_location_fails(client, db):
    _, token, draft_id = register_setup(client, locations=["Austin, TX", "Dallas, TX"])
    job_id = UUID(create_job(client, token, draft_id).json()["id"])

    await process_job(db, db.get(SearchJob, job_id), FakeGeocoder(), FakeLeadSource("dallas tx"))
    db.expire_all()
    job = db.get(SearchJob, job_id)
    locations = list(db.scalars(select(SearchJobLocation).where(
        SearchJobLocation.search_job_id == job_id,
    ).order_by(SearchJobLocation.position)))

    assert job.status == "partially_completed"
    assert job.processed_locations == 2
    assert [item.status for item in locations] == ["completed", "failed"]
    assert locations[1].error_code == "lead_source_unavailable"


def test_lead_pagination_validates_bounds(client):
    _, token, draft_id = register_setup(client)
    job_id = create_job(client, token, draft_id).json()["id"]

    response = client.get(f"/api/v1/search-jobs/{job_id}/leads?page=0", headers=auth(token))

    assert response.status_code == 422
    assert response.json()["code"] == "validation_error"
