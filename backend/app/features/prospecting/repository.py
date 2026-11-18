from uuid import UUID

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.features.prospecting.models import OfferProfile, SearchDraft, SearchDraftLocation


def find_default_offer(db: Session, user_id: UUID) -> OfferProfile | None:
    return db.scalar(select(OfferProfile).where(
        OfferProfile.user_id == user_id,
        OfferProfile.is_default.is_(True),
    ))


def find_current_draft(db: Session, user_id: UUID) -> SearchDraft | None:
    return db.scalar(
        select(SearchDraft)
        .where(SearchDraft.user_id == user_id)
        .order_by(SearchDraft.updated_at.desc(), SearchDraft.created_at.desc())
        .limit(1),
    )


def list_locations(db: Session, draft_id: UUID) -> list[SearchDraftLocation]:
    return list(db.scalars(
        select(SearchDraftLocation)
        .where(SearchDraftLocation.search_draft_id == draft_id)
        .order_by(SearchDraftLocation.position),
    ))


def delete_locations(db: Session, draft_id: UUID) -> None:
    db.execute(delete(SearchDraftLocation).where(
        SearchDraftLocation.search_draft_id == draft_id,
    ))
