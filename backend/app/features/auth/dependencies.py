from typing import Annotated

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.db import get_db
from app.features.auth import service
from app.features.auth.models import AuthSession, User

bearer = HTTPBearer(auto_error=False)
DatabaseSession = Annotated[Session, Depends(get_db)]


def get_current_auth(
    db: DatabaseSession,
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer)],
) -> tuple[User, AuthSession]:
    if credentials is None:
        raise service.unauthorized()
    return service.authenticate(db, credentials.credentials)


CurrentAuth = Annotated[tuple[User, AuthSession], Depends(get_current_auth)]
