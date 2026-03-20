from fastapi import APIRouter
from app.api.routers import (
    auth,
    users,
    pets,
    topics,
    chat,
    history,
    recommendations,
    notifications,
    settings,
)

api_v1_router = APIRouter()

api_v1_router.include_router(auth.router, prefix="/auth", tags=["Auth"])
api_v1_router.include_router(users.router, prefix="/users", tags=["Users"])
api_v1_router.include_router(pets.router, prefix="/pets", tags=["Pets"])
api_v1_router.include_router(topics.router, prefix="/topics", tags=["Topics"])
api_v1_router.include_router(chat.router, prefix="/chat", tags=["Chat"])
api_v1_router.include_router(history.router, prefix="/history", tags=["History"])
api_v1_router.include_router(recommendations.router, prefix="/recommendations", tags=["Recommendations"])
api_v1_router.include_router(notifications.router, prefix="/notifications", tags=["Notifications"])
api_v1_router.include_router(settings.router, prefix="/settings", tags=["Settings"])
