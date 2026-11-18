from math import ceil
from uuid import UUID

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.exceptions import ConflictError, NotFoundError
from app.features.discovery import repository
from app.features.discovery.models import SearchJob, SearchJobLocation
from app.features.discovery.schemas import (
    JobLocationResponse,
    LeadPageResponse,
    LeadResponse,
    SearchJobResponse,
)


def job_response(db: Session, job: SearchJob) -> SearchJobResponse:
    locations = repository.list_job_locations(db, job.id)
    return SearchJobResponse(
        id=job.id,
        search_draft_id=job.search_draft_id,
        provider=job.provider,
        status=job.status,
        category=job.category_snapshot,
        result_limit_per_location=job.result_limit_snapshot,
        total_locations=job.total_locations,
        processed_locations=job.processed_locations,
        businesses_found=job.businesses_found,
        error_message=job.error_message,
        locations=[JobLocationResponse(
            id=item.id,
            location_query=item.location_query,
            position=item.position,
            status=item.status,
            businesses_found=item.businesses_found,
            error_code=item.error_code,
            error_message=item.error_message,
        ) for item in locations],
        started_at=job.started_at,
        completed_at=job.completed_at,
        created_at=job.created_at,
        updated_at=job.updated_at,
    )


def create_job(db: Session, user_id: UUID, draft_id: UUID) -> SearchJobResponse:
    draft = repository.get_owned_draft(db, user_id, draft_id)
    if draft is None:
        raise NotFoundError("Search setup was not found", code="search_draft_not_found")
    draft_locations = repository.list_draft_locations(db, draft.id)
    if not draft_locations:
        raise ConflictError("Add a location before starting a search", code="search_has_no_locations")
    if repository.find_active_job(db, user_id):
        raise ConflictError(
            "Finish or cancel the active search before starting another",
            code="active_search_exists",
        )
    job = SearchJob(
        user_id=user_id,
        search_draft_id=draft.id,
        provider="openstreetmap",
        status="queued",
        category_snapshot=draft.business_category,
        result_limit_snapshot=draft.result_limit_per_location or 20,
        total_locations=len(draft_locations),
        processed_locations=0,
        businesses_found=0,
    )
    try:
        db.add(job)
        db.flush()
        db.add_all([SearchJobLocation(
            search_job_id=job.id,
            location_query=item.location_query,
            position=item.position,
            status="pending",
            businesses_found=0,
        ) for item in draft_locations])
        db.commit()
    except IntegrityError:
        db.rollback()
        raise ConflictError("The search could not be queued", code="search_job_conflict") from None
    db.refresh(job)
    return job_response(db, job)


def get_job(db: Session, user_id: UUID, job_id: UUID) -> SearchJobResponse:
    job = repository.get_owned_job(db, user_id, job_id)
    if job is None:
        raise NotFoundError("Search job was not found", code="search_job_not_found")
    return job_response(db, job)


def list_leads(
    db: Session, user_id: UUID, job_id: UUID, page: int, page_size: int,
) -> LeadPageResponse:
    job = repository.get_owned_job(db, user_id, job_id)
    if job is None:
        raise NotFoundError("Search job was not found", code="search_job_not_found")
    rows, total = repository.list_leads(db, job.id, page, page_size)
    return LeadPageResponse(
        items=[LeadResponse(
            id=lead.id,
            business_id=business.id,
            name=business.canonical_name,
            category=lead.matched_category,
            address=business.address,
            city=business.city,
            region=business.region,
            country_code=business.country_code,
            phone=business.phone,
            website_url=business.website_url,
            latitude=float(business.latitude) if business.latitude is not None else None,
            longitude=float(business.longitude) if business.longitude is not None else None,
            position=lead.position,
            duplicate_status=lead.duplicate_status,
            match_reason=lead.match_reason,
            match_confidence=lead.match_confidence,
        ) for lead, business in rows],
        page=page,
        page_size=page_size,
        total=total,
        pages=ceil(total / page_size) if total else 0,
    )
