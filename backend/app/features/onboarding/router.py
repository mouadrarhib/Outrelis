from fastapi import APIRouter, Response

from app.features.auth.dependencies import CurrentAuth, DatabaseSession
from app.features.onboarding import service
from app.features.onboarding.models import UserOnboarding
from app.features.onboarding.schemas import (
    OnboardingStateResponse,
    StartingPathRequest,
)

router = APIRouter(prefix="/onboarding", tags=["Onboarding"])


def state_response(onboarding: UserOnboarding | None) -> OnboardingStateResponse:
    if onboarding is None:
        return OnboardingStateResponse(
            starting_path=None,
            completed=False,
            completed_at=None,
            updated_at=None,
        )
    return OnboardingStateResponse(
        starting_path=onboarding.starting_path,
        completed=True,
        completed_at=onboarding.completed_at,
        updated_at=onboarding.updated_at,
    )


@router.get("", response_model=OnboardingStateResponse)
def get_onboarding(response: Response, db: DatabaseSession, auth: CurrentAuth):
    response.headers["Cache-Control"] = "no-store"
    return state_response(service.get_state(db, auth[0].id))


@router.put("/starting-path", response_model=OnboardingStateResponse)
def save_starting_path(
    data: StartingPathRequest,
    response: Response,
    db: DatabaseSession,
    auth: CurrentAuth,
):
    response.headers["Cache-Control"] = "no-store"
    return state_response(
        service.choose_starting_path(db, auth[0].id, data.starting_path),
    )
