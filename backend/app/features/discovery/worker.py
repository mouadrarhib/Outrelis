import asyncio
from datetime import UTC, datetime

from sqlalchemy import func, select
from sqlalchemy.orm import Session, sessionmaker

from app.config import get_settings
from app.db import get_engine
from app.features.discovery import repository
from app.features.discovery.deduplication.matcher import find_match
from app.features.discovery.deduplication.normalizers import (
    normalize_domain,
    normalize_name,
    normalize_phone,
    normalize_text,
)
from app.features.discovery.models import (
    Business,
    BusinessSource,
    GeocodedLocation,
    SearchJob,
    SearchJobLead,
    SearchJobLocation,
)
from app.features.discovery.providers.base import Geocoder, LeadSource, ProviderError
from app.features.discovery.providers.nominatim import NominatimClient
from app.features.discovery.providers.overpass import OverpassClient


def save_business(db: Session, item, job: SearchJob, location: SearchJobLocation, position: int):
    match = find_match(db, item)
    business = match.business if match.business and not match.possible_duplicate else None
    duplicate_status = "possible_duplicate" if match.possible_duplicate else (
        "existing" if business else "new"
    )
    if business is None:
        business = Business(
            canonical_name=item.name,
            normalized_name=normalize_name(item.name),
            website_url=item.website_url,
            website_domain=normalize_domain(item.website_url),
            phone=item.phone,
            normalized_phone=normalize_phone(item.phone),
            address=item.address,
            city=item.city,
            region=item.region,
            postal_code=item.postal_code,
            country_code=item.country_code,
            latitude=item.latitude,
            longitude=item.longitude,
            business_status=item.business_status,
        )
        db.add(business)
        db.flush()
    source_pair = repository.find_business_by_source(
        db, item.provider, item.source_type, item.source_id,
    )
    if source_pair:
        source_pair[1].last_seen_at = datetime.now(UTC)
        source_pair[1].raw_data = item.raw_data
    else:
        db.add(BusinessSource(
            business_id=business.id,
            provider=item.provider,
            source_type=item.source_type,
            source_id=item.source_id,
            source_url=item.source_url,
            category=item.category,
            rating=item.rating,
            review_count=item.review_count,
            opening_hours=item.opening_hours,
            raw_data=item.raw_data,
        ))
    existing_lead = db.scalar(select(SearchJobLead).where(
        SearchJobLead.search_job_id == job.id,
        SearchJobLead.business_id == business.id,
    ))
    if existing_lead is None:
        db.add(SearchJobLead(
            search_job_id=job.id,
            search_job_location_id=location.id,
            business_id=business.id,
            matched_category=job.category_snapshot,
            position=position,
            duplicate_status=duplicate_status,
            match_reason=match.reason,
            match_confidence=match.confidence,
        ))


async def process_location(
    db: Session, job: SearchJob, location: SearchJobLocation,
    geocoder: Geocoder, lead_source: LeadSource,
) -> None:
    try:
        location.status = "geocoding"
        location.started_at = datetime.now(UTC)
        db.commit()
        normalized = normalize_text(location.location_query) or location.location_query.casefold()
        geocoded = repository.get_cached_location(db, "nominatim", normalized)
        if geocoded is None:
            result = await geocoder.geocode(location.location_query)
            geocoded = GeocodedLocation(**result.__dict__)
            db.add(geocoded)
            db.flush()
        location.geocoded_location_id = geocoded.id
        location.status = "searching"
        db.commit()
        items = await lead_source.search(
            job.category_snapshot, geocoded, job.result_limit_snapshot or 20,
        )
        for position, item in enumerate(items, start=1):
            save_business(db, item, job, location, position)
        db.flush()
        location.businesses_found = len(items)
        location.status = "completed"
        location.completed_at = datetime.now(UTC)
        location.error_code = None
        location.error_message = None
        db.commit()
    except ProviderError as error:
        db.rollback()
        location = db.get(SearchJobLocation, location.id)
        location.status = "failed"
        location.error_code = error.code
        location.error_message = error.detail
        location.completed_at = datetime.now(UTC)
        db.commit()
    except Exception:
        db.rollback()
        location = db.get(SearchJobLocation, location.id)
        location.status = "failed"
        location.error_code = "search_processing_failed"
        location.error_message = "This location could not be processed"
        location.completed_at = datetime.now(UTC)
        db.commit()


async def process_job(
    db: Session, job: SearchJob, geocoder: Geocoder, lead_source: LeadSource,
) -> None:
    job.status = "running"
    job.started_at = job.started_at or datetime.now(UTC)
    db.commit()
    for location in repository.list_job_locations(db, job.id):
        if location.status == "completed":
            continue
        await process_location(db, job, location, geocoder, lead_source)
        db.refresh(job)
        job.processed_locations = len([
            item for item in repository.list_job_locations(db, job.id)
            if item.status in ("completed", "failed")
        ])
        job.businesses_found = db.scalar(select(func.count()).select_from(SearchJobLead).where(
            SearchJobLead.search_job_id == job.id,
        )) or 0
        db.commit()
    locations = repository.list_job_locations(db, job.id)
    failures = sum(item.status == "failed" for item in locations)
    job.status = "failed" if failures == len(locations) else (
        "partially_completed" if failures else "completed"
    )
    job.completed_at = datetime.now(UTC)
    job.error_message = "Some locations could not be processed" if failures else None
    db.commit()


async def run_once() -> bool:
    settings = get_settings()
    if "configure@example.com" in settings.osm_user_agent or "YOUR_EMAIL" in settings.osm_user_agent:
        raise RuntimeError("Configure OSM_USER_AGENT with a real contact before starting the worker")
    factory = sessionmaker(bind=get_engine())
    with factory() as db:
        job = repository.claim_next_job(db)
        if job is None:
            db.rollback()
            return False
        job.status = "running"
        job.started_at = datetime.now(UTC)
        db.commit()
        await process_job(
            db,
            job,
            NominatimClient(settings.nominatim_base_url, settings.osm_user_agent),
            OverpassClient(settings.overpass_base_url, settings.osm_user_agent),
        )
        return True


async def main() -> None:
    while True:
        worked = await run_once()
        if not worked:
            await asyncio.sleep(2)


if __name__ == "__main__":
    asyncio.run(main())
