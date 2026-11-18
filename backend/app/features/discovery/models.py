from datetime import datetime
from decimal import Decimal
from uuid import UUID, uuid4

from sqlalchemy import (
    BigInteger,
    CheckConstraint,
    DateTime,
    ForeignKey,
    ForeignKeyConstraint,
    Index,
    Integer,
    Numeric,
    SmallInteger,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base


class SearchJob(Base):
    __tablename__ = "search_jobs"
    __table_args__ = (
        ForeignKeyConstraint(
            ["search_draft_id", "user_id"],
            ["search_drafts.id", "search_drafts.user_id"],
            name="fk_search_jobs_draft_owner",
            ondelete="CASCADE",
        ),
        CheckConstraint(
            "status IN ('queued', 'running', 'completed', "
            "'partially_completed', 'failed', 'cancelled')",
            name="ck_search_jobs_status",
        ),
        CheckConstraint("btrim(provider) <> ''", name="ck_search_jobs_provider"),
        CheckConstraint(
            "btrim(category_snapshot) <> ''",
            name="ck_search_jobs_category_snapshot",
        ),
        CheckConstraint(
            "result_limit_snapshot IS NULL OR result_limit_snapshot > 0",
            name="ck_search_jobs_positive_result_limit",
        ),
        CheckConstraint(
            "total_locations > 0 AND processed_locations BETWEEN 0 AND total_locations",
            name="ck_search_jobs_location_counts",
        ),
        CheckConstraint("businesses_found >= 0", name="ck_search_jobs_business_count"),
        UniqueConstraint("id", "user_id", name="uq_search_jobs_id_user_id"),
        Index("ix_search_jobs_status_created_at", "status", "created_at"),
    )

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(index=True)
    search_draft_id: Mapped[UUID] = mapped_column(index=True)
    provider: Mapped[str] = mapped_column(String(40), default="openstreetmap")
    status: Mapped[str] = mapped_column(String(30), default="queued")
    category_snapshot: Mapped[str] = mapped_column(String(150))
    result_limit_snapshot: Mapped[int | None] = mapped_column(Integer)
    total_locations: Mapped[int] = mapped_column(SmallInteger)
    processed_locations: Mapped[int] = mapped_column(SmallInteger, default=0)
    businesses_found: Mapped[int] = mapped_column(Integer, default=0)
    error_message: Mapped[str | None] = mapped_column(Text)
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class GeocodedLocation(Base):
    __tablename__ = "geocoded_locations"
    __table_args__ = (
        CheckConstraint("btrim(provider) <> ''", name="ck_geocoded_locations_provider"),
        CheckConstraint(
            "btrim(normalized_query) <> ''",
            name="ck_geocoded_locations_normalized_query",
        ),
        CheckConstraint(
            "latitude BETWEEN -90 AND 90 AND longitude BETWEEN -180 AND 180",
            name="ck_geocoded_locations_coordinates",
        ),
        UniqueConstraint(
            "provider", "normalized_query", name="uq_geocoded_locations_provider_query"
        ),
    )

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    provider: Mapped[str] = mapped_column(String(40), default="nominatim")
    normalized_query: Mapped[str] = mapped_column(String(200))
    display_name: Mapped[str] = mapped_column(String(500))
    osm_type: Mapped[str | None] = mapped_column(String(20))
    osm_id: Mapped[int | None] = mapped_column(BigInteger)
    osm_area_id: Mapped[int | None] = mapped_column(BigInteger)
    latitude: Mapped[Decimal] = mapped_column(Numeric(9, 6))
    longitude: Mapped[Decimal] = mapped_column(Numeric(10, 6))
    bounding_box: Mapped[dict] = mapped_column(JSONB)
    country_code: Mapped[str | None] = mapped_column(String(2))
    raw_data: Mapped[dict] = mapped_column(JSONB)
    resolved_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


class SearchJobLocation(Base):
    __tablename__ = "search_job_locations"
    __table_args__ = (
        CheckConstraint(
            "status IN ('pending', 'geocoding', 'searching', 'completed', 'failed')",
            name="ck_search_job_locations_status",
        ),
        CheckConstraint(
            "btrim(location_query) <> ''",
            name="ck_search_job_locations_query",
        ),
        CheckConstraint("position BETWEEN 1 AND 10", name="ck_search_job_locations_position"),
        CheckConstraint(
            "businesses_found >= 0", name="ck_search_job_locations_business_count"
        ),
        UniqueConstraint("id", "search_job_id", name="uq_search_job_locations_id_job"),
        UniqueConstraint(
            "search_job_id", "position", name="uq_search_job_locations_position"
        ),
    )

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    search_job_id: Mapped[UUID] = mapped_column(
        ForeignKey("search_jobs.id", ondelete="CASCADE"), index=True
    )
    geocoded_location_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("geocoded_locations.id", ondelete="SET NULL"), index=True
    )
    location_query: Mapped[str] = mapped_column(String(200))
    position: Mapped[int] = mapped_column(SmallInteger)
    status: Mapped[str] = mapped_column(String(20), default="pending")
    businesses_found: Mapped[int] = mapped_column(Integer, default=0)
    error_code: Mapped[str | None] = mapped_column(String(80))
    error_message: Mapped[str | None] = mapped_column(Text)
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class Business(Base):
    __tablename__ = "businesses"
    __table_args__ = (
        CheckConstraint("btrim(canonical_name) <> ''", name="ck_businesses_canonical_name"),
        CheckConstraint("btrim(normalized_name) <> ''", name="ck_businesses_normalized_name"),
        CheckConstraint(
            "business_status IN ('active', 'closed', 'unknown')",
            name="ck_businesses_status",
        ),
        CheckConstraint(
            "(latitude IS NULL AND longitude IS NULL) OR "
            "(latitude BETWEEN -90 AND 90 AND longitude BETWEEN -180 AND 180)",
            name="ck_businesses_coordinates",
        ),
        Index("ix_businesses_website_domain", "website_domain"),
        Index("ix_businesses_normalized_phone", "normalized_phone"),
        Index("ix_businesses_normalized_name", "normalized_name"),
    )

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    canonical_name: Mapped[str] = mapped_column(String(300))
    normalized_name: Mapped[str] = mapped_column(String(300))
    website_url: Mapped[str | None] = mapped_column(String(2048))
    website_domain: Mapped[str | None] = mapped_column(String(255))
    phone: Mapped[str | None] = mapped_column(String(80))
    normalized_phone: Mapped[str | None] = mapped_column(String(32))
    address: Mapped[str | None] = mapped_column(String(500))
    city: Mapped[str | None] = mapped_column(String(150))
    region: Mapped[str | None] = mapped_column(String(150))
    postal_code: Mapped[str | None] = mapped_column(String(32))
    country_code: Mapped[str | None] = mapped_column(String(2))
    latitude: Mapped[Decimal | None] = mapped_column(Numeric(9, 6))
    longitude: Mapped[Decimal | None] = mapped_column(Numeric(10, 6))
    business_status: Mapped[str] = mapped_column(String(20), default="unknown")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class BusinessSource(Base):
    __tablename__ = "business_sources"
    __table_args__ = (
        CheckConstraint("btrim(provider) <> ''", name="ck_business_sources_provider"),
        CheckConstraint("btrim(source_type) <> ''", name="ck_business_sources_source_type"),
        CheckConstraint("btrim(source_id) <> ''", name="ck_business_sources_source_id"),
        CheckConstraint("rating IS NULL OR rating BETWEEN 0 AND 5", name="ck_business_sources_rating"),
        CheckConstraint(
            "review_count IS NULL OR review_count >= 0",
            name="ck_business_sources_review_count",
        ),
        UniqueConstraint(
            "provider", "source_type", "source_id", name="uq_business_sources_identity"
        ),
    )

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    business_id: Mapped[UUID] = mapped_column(
        ForeignKey("businesses.id", ondelete="CASCADE"), index=True
    )
    provider: Mapped[str] = mapped_column(String(40))
    source_type: Mapped[str] = mapped_column(String(30))
    source_id: Mapped[str] = mapped_column(String(255))
    source_url: Mapped[str | None] = mapped_column(String(2048))
    category: Mapped[str | None] = mapped_column(String(150))
    rating: Mapped[Decimal | None] = mapped_column(Numeric(2, 1))
    review_count: Mapped[int | None] = mapped_column(Integer)
    opening_hours: Mapped[dict | None] = mapped_column(JSONB)
    raw_data: Mapped[dict] = mapped_column(JSONB)
    first_seen_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    last_seen_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class SearchJobLead(Base):
    __tablename__ = "search_job_leads"
    __table_args__ = (
        ForeignKeyConstraint(
            ["search_job_location_id", "search_job_id"],
            ["search_job_locations.id", "search_job_locations.search_job_id"],
            name="fk_search_job_leads_location_job",
            ondelete="CASCADE",
        ),
        CheckConstraint("position > 0", name="ck_search_job_leads_position"),
        CheckConstraint(
            "duplicate_status IN ('new', 'existing', 'possible_duplicate')",
            name="ck_search_job_leads_duplicate_status",
        ),
        CheckConstraint(
            "match_confidence BETWEEN 0 AND 100",
            name="ck_search_job_leads_match_confidence",
        ),
        UniqueConstraint("search_job_id", "business_id", name="uq_search_job_leads_business"),
        UniqueConstraint(
            "search_job_location_id", "position", name="uq_search_job_leads_position"
        ),
    )

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    search_job_id: Mapped[UUID] = mapped_column(
        ForeignKey("search_jobs.id", ondelete="CASCADE"), index=True
    )
    search_job_location_id: Mapped[UUID] = mapped_column(index=True)
    business_id: Mapped[UUID] = mapped_column(
        ForeignKey("businesses.id", ondelete="CASCADE"), index=True
    )
    matched_category: Mapped[str] = mapped_column(String(150))
    position: Mapped[int] = mapped_column(Integer)
    duplicate_status: Mapped[str] = mapped_column(String(30), default="new")
    match_reason: Mapped[str] = mapped_column(String(80))
    match_confidence: Mapped[int] = mapped_column(SmallInteger)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
