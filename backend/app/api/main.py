from fastapi import APIRouter

from app.api.routes import tasks
from app.api.routes import agent

api_router = APIRouter()

api_router.include_router(tasks.router)
api_router.include_router(agent.router)
