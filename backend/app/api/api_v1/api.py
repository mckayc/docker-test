from fastapi import APIRouter
from app.api.api_v1.endpoints import auth, users, tasks, game

api_router = APIRouter()

api_router.include_router(auth.router, tags=["authentication"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(tasks.router, prefix="/tasks", tags=["tasks"])
api_router.include_router(game.router, prefix="/game", tags=["game"]) 