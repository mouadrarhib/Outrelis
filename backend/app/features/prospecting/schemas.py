import re
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


def clean_text(value: object) -> object:
    return " ".join(value.split()) if isinstance(value, str) else value


class ProspectingSetupRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    service_name: str = Field(min_length=1, max_length=120)
    outreach_language: str = Field(min_length=2, max_length=35)
    business_category: str = Field(min_length=1, max_length=150)
    locations: list[str] = Field(min_length=1, max_length=10)
    result_limit_per_location: int | None = Field(default=None, ge=1, le=100)

    @field_validator("service_name", "outreach_language", "business_category", mode="before")
    @classmethod
    def normalize_text(cls, value: object) -> object:
        return clean_text(value)

    @field_validator("outreach_language")
    @classmethod
    def validate_language(cls, value: str) -> str:
        if not re.fullmatch(r"[A-Za-z]{2,8}(?:-[A-Za-z0-9]{1,8})*", value):
            raise ValueError("Use a valid language tag such as en, es, or en-US")
        return value

    @field_validator("locations", mode="before")
    @classmethod
    def normalize_locations(cls, value: object) -> object:
        if not isinstance(value, list):
            return value
        return [clean_text(location) for location in value]

    @model_validator(mode="after")
    def validate_locations(self):
        if any(not location or len(location) > 200 for location in self.locations):
            raise ValueError("Each location must contain 1–200 characters")
        normalized = [location.casefold() for location in self.locations]
        if len(set(normalized)) != len(normalized):
            raise ValueError("Locations must be unique")
        return self


class OfferProfileResponse(BaseModel):
    id: UUID
    service_name: str
    outreach_language: str
    is_default: bool
    created_at: datetime
    updated_at: datetime


class SearchDraftLocationResponse(BaseModel):
    id: UUID
    location_query: str
    position: int


class SearchDraftResponse(BaseModel):
    id: UUID
    offer_profile_id: UUID
    business_category: str
    result_limit_per_location: int | None
    locations: list[SearchDraftLocationResponse]
    created_at: datetime
    updated_at: datetime


class ProspectingSetupResponse(BaseModel):
    configured: bool
    offer_profile: OfferProfileResponse | None
    search_draft: SearchDraftResponse | None
