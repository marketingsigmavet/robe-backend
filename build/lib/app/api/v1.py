from fastapi import APIRouter

from app.api.routers.health import router as health_router

api_v1_router = APIRouter(prefix="/api/v1", tags=["api-v1"])

api_v1_router.include_router(health_router)

