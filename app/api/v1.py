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
    admin_species,
    admin_breeds,
    admin_roles,
    admin_topics,
    admin_product_brands,
    admin_product_categories,
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
api_v1_router.include_router(admin_species.router, prefix="/admin/species", tags=["Admin", "Pet Species"])
api_v1_router.include_router(admin_breeds.router, prefix="/admin/breeds", tags=["Admin", "Breeds"])
api_v1_router.include_router(admin_roles.router, prefix="/admin/roles", tags=["Admin", "Roles"])
api_v1_router.include_router(admin_topics.router, prefix="/admin/topics", tags=["Admin", "Topics"])
api_v1_router.include_router(admin_product_brands.router, prefix="/admin/product-brands", tags=["Admin", "Product Brands"])
api_v1_router.include_router(admin_product_categories.router, prefix="/admin/product-categories", tags=["Admin", "Product Categories"])
