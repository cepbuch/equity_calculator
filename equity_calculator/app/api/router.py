from fastapi import APIRouter

from app.api.v1.health import router as health_router
from app.api.v1.timelines import router as timeline_router

api_v1_router = APIRouter()
api_v1_router.include_router(timeline_router, prefix='/timelines')
api_v1_router.include_router(health_router, prefix='/health')
