from fastapi import APIRouter, Response

from app.features.auth.dependencies import CurrentAuth, DatabaseSession
from app.features.prospecting import service
from app.features.prospecting.schemas import ProspectingSetupRequest, ProspectingSetupResponse

router = APIRouter(prefix="/prospecting", tags=["Prospecting"])


@router.get("/setup", response_model=ProspectingSetupResponse)
def get_setup(response: Response, db: DatabaseSession, auth: CurrentAuth):
    response.headers["Cache-Control"] = "no-store"
    return service.get_setup(db, auth[0].id)


@router.put("/setup", response_model=ProspectingSetupResponse)
def save_setup(
    data: ProspectingSetupRequest,
    response: Response,
    db: DatabaseSession,
    auth: CurrentAuth,
):
    response.headers["Cache-Control"] = "no-store"
    return service.save_setup(db, auth[0].id, data)
