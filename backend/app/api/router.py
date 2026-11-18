from fastapi import APIRouter

from app.features.auth.router import router as auth_router
from app.features.discovery.router import router as discovery_router
from app.features.onboarding.router import router as onboarding_router
from app.features.prospecting.router import router as prospecting_router

router = APIRouter(prefix="/api/v1")
router.include_router(auth_router)
router.include_router(discovery_router)
router.include_router(onboarding_router)
router.include_router(prospecting_router)
