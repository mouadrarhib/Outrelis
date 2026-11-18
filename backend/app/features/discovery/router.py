from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Query, Response, status

from app.features.auth.dependencies import CurrentAuth, DatabaseSession
from app.features.discovery import service
from app.features.discovery.schemas import (
    CreateSearchJobRequest,
    LeadPageResponse,
    SearchJobResponse,
)

router = APIRouter(prefix="/search-jobs", tags=["Lead discovery"])


@router.post("", response_model=SearchJobResponse, status_code=status.HTTP_201_CREATED)
def create_search_job(
    data: CreateSearchJobRequest,
    response: Response,
    db: DatabaseSession,
    auth: CurrentAuth,
):
    response.headers["Cache-Control"] = "no-store"
    return service.create_job(db, auth[0].id, data.search_draft_id)


@router.get("/{job_id}", response_model=SearchJobResponse)
def get_search_job(job_id: UUID, response: Response, db: DatabaseSession, auth: CurrentAuth):
    response.headers["Cache-Control"] = "no-store"
    return service.get_job(db, auth[0].id, job_id)


@router.get("/{job_id}/leads", response_model=LeadPageResponse)
def list_search_job_leads(
    job_id: UUID,
    response: Response,
    db: DatabaseSession,
    auth: CurrentAuth,
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=100)] = 20,
):
    response.headers["Cache-Control"] = "no-store"
    return service.list_leads(db, auth[0].id, job_id, page, page_size)
