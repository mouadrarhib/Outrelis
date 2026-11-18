from uuid import UUID

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.features.discovery.models import (
    Business,
    BusinessSource,
    GeocodedLocation,
    SearchJob,
    SearchJobLead,
    SearchJobLocation,
)
from app.features.prospecting.models import SearchDraft, SearchDraftLocation


def get_owned_draft(db: Session, user_id: UUID, draft_id: UUID) -> SearchDraft | None:
    return db.scalar(select(SearchDraft).where(
        SearchDraft.id == draft_id, SearchDraft.user_id == user_id,
    ))


def list_draft_locations(db: Session, draft_id: UUID) -> list[SearchDraftLocation]:
    return list(db.scalars(select(SearchDraftLocation).where(
        SearchDraftLocation.search_draft_id == draft_id,
    ).order_by(SearchDraftLocation.position)))


def find_active_job(db: Session, user_id: UUID) -> SearchJob | None:
    return db.scalar(select(SearchJob).where(
        SearchJob.user_id == user_id,
        SearchJob.status.in_(("queued", "running")),
    ).limit(1))


def get_owned_job(db: Session, user_id: UUID, job_id: UUID) -> SearchJob | None:
    return db.scalar(select(SearchJob).where(
        SearchJob.id == job_id, SearchJob.user_id == user_id,
    ))


def list_job_locations(db: Session, job_id: UUID) -> list[SearchJobLocation]:
    return list(db.scalars(select(SearchJobLocation).where(
        SearchJobLocation.search_job_id == job_id,
    ).order_by(SearchJobLocation.position)))


def claim_next_job(db: Session) -> SearchJob | None:
    return db.scalar(
        select(SearchJob)
        .where(SearchJob.status == "queued")
        .order_by(SearchJob.created_at)
        .with_for_update(skip_locked=True)
        .limit(1)
    )


def get_cached_location(
    db: Session, provider: str, normalized_query: str,
) -> GeocodedLocation | None:
    return db.scalar(select(GeocodedLocation).where(
        GeocodedLocation.provider == provider,
        GeocodedLocation.normalized_query == normalized_query,
        or_(GeocodedLocation.expires_at.is_(None), GeocodedLocation.expires_at > func.now()),
    ))


def find_business_by_source(
    db: Session, provider: str, source_type: str, source_id: str,
) -> tuple[Business, BusinessSource] | None:
    row = db.execute(
        select(Business, BusinessSource)
        .join(BusinessSource, BusinessSource.business_id == Business.id)
        .where(
            BusinessSource.provider == provider,
            BusinessSource.source_type == source_type,
            BusinessSource.source_id == source_id,
        )
    ).first()
    return (row[0], row[1]) if row else None


def find_business_by_domain(db: Session, domain: str) -> Business | None:
    return db.scalar(select(Business).where(Business.website_domain == domain).limit(1))


def find_business_by_phone(db: Session, phone: str) -> Business | None:
    return db.scalar(select(Business).where(Business.normalized_phone == phone).limit(1))


def find_business_candidates(
    db: Session, city: str | None, region: str | None, country_code: str | None,
) -> list[Business]:
    query = select(Business)
    if country_code:
        query = query.where(Business.country_code == country_code)
    if region:
        query = query.where(Business.region == region)
    if city:
        query = query.where(Business.city == city)
    return list(db.scalars(query.limit(200)))


def list_leads(
    db: Session, job_id: UUID, page: int, page_size: int,
) -> tuple[list[tuple[SearchJobLead, Business]], int]:
    condition = SearchJobLead.search_job_id == job_id
    total = db.scalar(select(func.count()).select_from(SearchJobLead).where(condition)) or 0
    rows = db.execute(
        select(SearchJobLead, Business)
        .join(Business, Business.id == SearchJobLead.business_id)
        .where(condition)
        .order_by(SearchJobLead.position, SearchJobLead.created_at)
        .offset((page - 1) * page_size)
        .limit(page_size)
    ).all()
    return [(row[0], row[1]) for row in rows], total
