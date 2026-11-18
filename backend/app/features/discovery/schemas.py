from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class CreateSearchJobRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    search_draft_id: UUID


class JobLocationResponse(BaseModel):
    id: UUID
    location_query: str
    position: int
    status: str
    businesses_found: int
    error_code: str | None
    error_message: str | None


class SearchJobResponse(BaseModel):
    id: UUID
    search_draft_id: UUID
    provider: str
    status: str
    category: str
    result_limit_per_location: int | None
    total_locations: int
    processed_locations: int
    businesses_found: int
    error_message: str | None
    locations: list[JobLocationResponse]
    started_at: datetime | None
    completed_at: datetime | None
    created_at: datetime
    updated_at: datetime


class LeadResponse(BaseModel):
    id: UUID
    business_id: UUID
    name: str
    category: str
    address: str | None
    city: str | None
    region: str | None
    country_code: str | None
    phone: str | None
    website_url: str | None
    latitude: float | None
    longitude: float | None
    position: int
    duplicate_status: str
    match_reason: str
    match_confidence: int


class LeadPageResponse(BaseModel):
    items: list[LeadResponse]
    page: int
    page_size: int
    total: int
    pages: int


class LeadPageQuery(BaseModel):
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)
