from decimal import Decimal
from uuid import UUID

import pytest
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError

from app.features.discovery.models import (
    Business,
    BusinessSource,
    GeocodedLocation,
    SearchJob,
    SearchJobLead,
    SearchJobLocation,
)
from app.features.prospecting.models import SearchDraft

PASSWORD = "a long private passphrase"


def create_setup(client, db, email: str) -> tuple[UUID, SearchDraft]:
    registration = client.post(
        "/api/v1/auth/register",
        json={"full_name": "Search Owner", "email": email, "password": PASSWORD},
    )
    assert registration.status_code == 201
    login = client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": PASSWORD},
    )
    assert login.status_code == 200
    response = client.put(
        "/api/v1/prospecting/setup",
        headers={"Authorization": f"Bearer {login.json()['access_token']}"},
        json={
            "service_name": "Website design",
            "outreach_language": "en-US",
            "business_category": "Dental clinics",
            "locations": ["Austin, TX"],
            "result_limit_per_location": 20,
        },
    )
    assert response.status_code == 200
    user_id = UUID(registration.json()["id"])
    draft = db.scalar(select(SearchDraft).where(SearchDraft.user_id == user_id))
    return user_id, draft


def create_discovery_graph(client, db):
    user_id, draft = create_setup(client, db, "discovery@example.com")
    job = SearchJob(
        user_id=user_id,
        search_draft_id=draft.id,
        provider="openstreetmap",
        status="running",
        category_snapshot="Dental clinics",
        result_limit_snapshot=20,
        total_locations=1,
        processed_locations=0,
        businesses_found=0,
    )
    geocoded = GeocodedLocation(
        provider="nominatim",
        normalized_query="austin, tx",
        display_name="Austin, Travis County, Texas, United States",
        osm_type="relation",
        osm_id=113314,
        osm_area_id=3600113314,
        latitude=Decimal("30.267153"),
        longitude=Decimal("-97.743057"),
        bounding_box={"south": "30.098", "north": "30.516"},
        country_code="us",
        raw_data={"osm_id": 113314},
    )
    business = Business(
        canonical_name="Example Dental",
        normalized_name="example dental",
        website_url="https://example-dental.test",
        website_domain="example-dental.test",
        phone="+1 512-555-0198",
        normalized_phone="+15125550198",
        city="Austin",
        region="TX",
        country_code="us",
        latitude=Decimal("30.267200"),
        longitude=Decimal("-97.743100"),
        business_status="active",
    )
    db.add_all([job, geocoded, business])
    db.flush()
    job_location = SearchJobLocation(
        search_job_id=job.id,
        geocoded_location_id=geocoded.id,
        location_query="Austin, TX",
        position=1,
        status="completed",
        businesses_found=1,
    )
    source = BusinessSource(
        business_id=business.id,
        provider="openstreetmap",
        source_type="node",
        source_id="123456789",
        source_url="https://www.openstreetmap.org/node/123456789",
        category="dentist",
        raw_data={"type": "node", "id": 123456789},
    )
    db.add_all([job_location, source])
    db.flush()
    lead = SearchJobLead(
        search_job_id=job.id,
        search_job_location_id=job_location.id,
        business_id=business.id,
        matched_category="Dental clinics",
        position=1,
        duplicate_status="new",
        match_reason="new_business",
        match_confidence=100,
    )
    db.add(lead)
    db.commit()
    return job, geocoded, business, source, job_location, lead


def test_discovery_graph_persists_provenance_and_deduplicated_lead(client, db):
    job, geocoded, business, source, job_location, lead = create_discovery_graph(client, db)

    assert lead.search_job_id == job.id
    assert lead.search_job_location_id == job_location.id
    assert lead.business_id == business.id
    assert source.business_id == business.id
    assert source.raw_data["id"] == 123456789
    assert geocoded.osm_area_id == 3600113314
    assert db.scalar(select(func.count()).select_from(SearchJobLead)) == 1


def test_search_job_cannot_use_another_users_draft(client, db):
    first_user_id, _ = create_setup(client, db, "first-search@example.com")
    _, second_draft = create_setup(client, db, "second-search@example.com")
    db.add(SearchJob(
        user_id=first_user_id,
        search_draft_id=second_draft.id,
        provider="openstreetmap",
        status="queued",
        category_snapshot="Dental clinics",
        result_limit_snapshot=20,
        total_locations=1,
        processed_locations=0,
        businesses_found=0,
    ))

    with pytest.raises(IntegrityError):
        db.commit()
    db.rollback()


def test_provider_identity_is_unique_across_businesses(client, db):
    _, _, _, _, _, _ = create_discovery_graph(client, db)
    second_business = Business(
        canonical_name="Duplicate Dental",
        normalized_name="duplicate dental",
        business_status="unknown",
    )
    db.add(second_business)
    db.flush()
    db.add(BusinessSource(
        business_id=second_business.id,
        provider="openstreetmap",
        source_type="node",
        source_id="123456789",
        raw_data={"id": 123456789},
    ))

    with pytest.raises(IntegrityError):
        db.commit()
    db.rollback()


def test_deleting_job_cascades_results_but_preserves_canonical_business(client, db):
    job, _, business, source, _, _ = create_discovery_graph(client, db)

    db.delete(job)
    db.commit()

    assert db.scalar(select(func.count()).select_from(SearchJobLocation)) == 0
    assert db.scalar(select(func.count()).select_from(SearchJobLead)) == 0
    assert db.get(Business, business.id) is not None
    assert db.get(BusinessSource, source.id) is not None


def test_database_rejects_invalid_job_progress(client, db):
    user_id, draft = create_setup(client, db, "invalid-progress@example.com")
    db.add(SearchJob(
        user_id=user_id,
        search_draft_id=draft.id,
        provider="openstreetmap",
        status="running",
        category_snapshot="Dental clinics",
        result_limit_snapshot=20,
        total_locations=1,
        processed_locations=2,
        businesses_found=0,
    ))

    with pytest.raises(IntegrityError):
        db.commit()
    db.rollback()
