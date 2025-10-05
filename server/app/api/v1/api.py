from fastapi import APIRouter
from app.api.v1.endpoints import auth
from app.api.v1 import podcasts

api_router = APIRouter()

# Include auth routes
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])

# Include podcast routes
api_router.include_router(podcasts.router, tags=["podcasts"])
