from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    DateTime,
    ForeignKey,
    ForeignKeyConstraint,
    Index,
    SmallInteger,
    String,
    UniqueConstraint,
    func,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base


class OfferProfile(Base):
    __tablename__ = "offer_profiles"
    __table_args__ = (
        CheckConstraint("btrim(service_name) <> ''", name="ck_offer_profiles_service_name"),
        CheckConstraint(
            "btrim(outreach_language) <> ''",
            name="ck_offer_profiles_outreach_language",
        ),
        UniqueConstraint("id", "user_id", name="uq_offer_profiles_id_user_id"),
        Index(
            "uq_offer_profiles_default_per_user",
            "user_id",
            unique=True,
            postgresql_where=text("is_default"),
        ),
    )

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True,
    )
    service_name: Mapped[str] = mapped_column(String(120))
    outreach_language: Mapped[str] = mapped_column(String(35))
    is_default: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        server_default="true",
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )


class SearchDraft(Base):
    __tablename__ = "search_drafts"
    __table_args__ = (
        ForeignKeyConstraint(
            ["offer_profile_id", "user_id"],
            ["offer_profiles.id", "offer_profiles.user_id"],
            name="fk_search_drafts_offer_owner",
            ondelete="CASCADE",
        ),
        CheckConstraint(
            "btrim(business_category) <> ''",
            name="ck_search_drafts_business_category",
        ),
        CheckConstraint(
            "result_limit_per_location IS NULL OR result_limit_per_location > 0",
            name="ck_search_drafts_positive_result_limit",
        ),
        UniqueConstraint("id", "user_id", name="uq_search_drafts_id_user_id"),
    )

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(index=True)
    offer_profile_id: Mapped[UUID] = mapped_column(index=True)
    business_category: Mapped[str] = mapped_column(String(150))
    result_limit_per_location: Mapped[int | None] = mapped_column()
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )


class SearchDraftLocation(Base):
    __tablename__ = "search_draft_locations"
    __table_args__ = (
        CheckConstraint(
            "btrim(location_query) <> ''",
            name="ck_search_draft_locations_query",
        ),
        CheckConstraint(
            "btrim(normalized_location) <> ''",
            name="ck_search_draft_locations_normalized",
        ),
        CheckConstraint(
            "position BETWEEN 1 AND 10",
            name="ck_search_draft_locations_position",
        ),
        UniqueConstraint(
            "search_draft_id",
            "normalized_location",
            name="uq_search_draft_locations_normalized",
        ),
        UniqueConstraint(
            "search_draft_id",
            "position",
            name="uq_search_draft_locations_position",
        ),
    )

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    search_draft_id: Mapped[UUID] = mapped_column(
        ForeignKey("search_drafts.id", ondelete="CASCADE"),
        index=True,
    )
    location_query: Mapped[str] = mapped_column(String(200))
    normalized_location: Mapped[str] = mapped_column(String(200))
    position: Mapped[int] = mapped_column(SmallInteger)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )
