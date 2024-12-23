from fastapi import APIRouter, Depends, Request
from uuid import UUID

from src.app.controllers.users.handlers import UserHandler
from src.app.middleware.middleware import auth_middleware
from src.app.services.user_service import UserService
from src.app.models.request_objects import SignupRequest, LoginRequest


def create_user_routes(user_service: UserService) -> APIRouter:
    router = APIRouter(tags=["users"])
    user_handler = UserHandler.create(user_service)

    router.dependencies = [Depends(auth_middleware)]

    @router.get("/users")
    async def get_users(request: Request):
        return await user_handler.get_users(request)

    @router.get("/user/{user_id}")
    async def get_user(user_id: str):
        return await user_handler.get_user(user_id)

    @router.delete("/user/{user_id}")
    async def delete_user(request: Request, user_id: str):
        return await user_handler.delete_user(request, user_id)

    return router
