from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.exceptions import ConflictError
from app.features.prospecting import repository
from app.features.prospecting.models import OfferProfile, SearchDraft, SearchDraftLocation
from app.features.prospecting.schemas import (
    OfferProfileResponse,
    ProspectingSetupRequest,
    ProspectingSetupResponse,
    SearchDraftLocationResponse,
    SearchDraftResponse,
)


def response(
    offer: OfferProfile | None,
    draft: SearchDraft | None,
    locations: list[SearchDraftLocation] | None = None,
) -> ProspectingSetupResponse:
    if offer is None or draft is None:
        return ProspectingSetupResponse(
            configured=False,
            offer_profile=None,
            search_draft=None,
        )
    return ProspectingSetupResponse(
        configured=True,
        offer_profile=OfferProfileResponse(
            id=offer.id,
            service_name=offer.service_name,
            outreach_language=offer.outreach_language,
            is_default=offer.is_default,
            created_at=offer.created_at,
            updated_at=offer.updated_at,
        ),
        search_draft=SearchDraftResponse(
            id=draft.id,
            offer_profile_id=draft.offer_profile_id,
            business_category=draft.business_category,
            result_limit_per_location=draft.result_limit_per_location,
            locations=[SearchDraftLocationResponse(
                id=location.id,
                location_query=location.location_query,
                position=location.position,
            ) for location in locations or []],
            created_at=draft.created_at,
            updated_at=draft.updated_at,
        ),
    )


def get_setup(db: Session, user_id: UUID) -> ProspectingSetupResponse:
    offer = repository.find_default_offer(db, user_id)
    draft = repository.find_current_draft(db, user_id)
    locations = repository.list_locations(db, draft.id) if draft else []
    return response(offer, draft, locations)


def save_setup(
    db: Session,
    user_id: UUID,
    data: ProspectingSetupRequest,
) -> ProspectingSetupResponse:
    try:
        now = datetime.now(UTC)
        offer = repository.find_default_offer(db, user_id)
        if offer is None:
            offer = OfferProfile(
                user_id=user_id,
                service_name=data.service_name,
                outreach_language=data.outreach_language,
                is_default=True,
            )
            db.add(offer)
            db.flush()
        else:
            offer.service_name = data.service_name
            offer.outreach_language = data.outreach_language
            offer.updated_at = now

        draft = repository.find_current_draft(db, user_id)
        if draft is None:
            draft = SearchDraft(
                user_id=user_id,
                offer_profile_id=offer.id,
                business_category=data.business_category,
                result_limit_per_location=data.result_limit_per_location,
            )
            db.add(draft)
            db.flush()
        else:
            draft.offer_profile_id = offer.id
            draft.business_category = data.business_category
            draft.result_limit_per_location = data.result_limit_per_location
            draft.updated_at = now
            repository.delete_locations(db, draft.id)

        locations = [SearchDraftLocation(
            search_draft_id=draft.id,
            location_query=location,
            normalized_location=location.casefold(),
            position=position,
        ) for position, location in enumerate(data.locations, start=1)]
        db.add_all(locations)
        db.commit()
    except IntegrityError:
        db.rollback()
        raise ConflictError(
            "The prospecting setup changed while it was being saved",
            code="prospecting_setup_conflict",
        ) from None
    db.refresh(offer)
    db.refresh(draft)
    for location in locations:
        db.refresh(location)
    return response(offer, draft, locations)
