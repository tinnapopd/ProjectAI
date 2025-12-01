from fastapi import APIRouter

from api.routes import agent
from core.config import settings

api_router = APIRouter()
api_router.include_router(agent.router)

if settings.ENVIRONMENT == "local":
    print("INFO:     You are running in local environment")
    # You can add more local-development API routers here if needed
    pass
