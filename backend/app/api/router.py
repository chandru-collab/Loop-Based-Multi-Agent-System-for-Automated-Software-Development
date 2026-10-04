from fastapi import APIRouter
from app.api.routes import projects, agents, workflow, health

api_router = APIRouter()

api_router.include_router(health.router, tags=["health"])
api_router.include_router(projects.router, prefix="/projects", tags=["projects"])
api_router.include_router(agents.router, prefix="/projects", tags=["agents"])
api_router.include_router(workflow.router, prefix="/projects", tags=["workflow"])
