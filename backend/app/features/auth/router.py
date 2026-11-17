from fastapi import APIRouter, Request, Response

from app.features.auth import service
from app.features.auth.dependencies import CurrentAuth, DatabaseSession
from app.features.auth.schemas import LoginRequest, LoginResponse, RegisterRequest, UserResponse

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=UserResponse, status_code=201)
def register(data: RegisterRequest, request: Request, response: Response, db: DatabaseSession):
    response.headers["Cache-Control"] = "no-store"
    service.enforce_rate_limit(db, "register-ip", request.client.host if request.client else "unknown", 10)
    return service.register(db, data)


@router.post("/login", response_model=LoginResponse)
def login(data: LoginRequest, request: Request, response: Response, db: DatabaseSession):
    response.headers["Cache-Control"] = "no-store"
    service.enforce_rate_limit(db, "login-ip", request.client.host if request.client else "unknown", 30)
    service.enforce_rate_limit(db, "login-email", str(data.email), 10)
    user, token, lifetime = service.login(db, data)
    return LoginResponse(access_token=token, expires_in=lifetime, user=UserResponse.model_validate(user))


@router.get("/me", response_model=UserResponse)
def me(response: Response, auth: CurrentAuth):
    response.headers["Cache-Control"] = "no-store"
    return auth[0]


@router.post("/logout", status_code=204)
def logout(db: DatabaseSession, auth: CurrentAuth):
    service.logout(db, auth[1])
    return Response(status_code=204, headers={"Cache-Control": "no-store"})
