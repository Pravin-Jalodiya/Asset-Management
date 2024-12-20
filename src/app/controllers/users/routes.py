from fastapi import APIRouter, Depends, Request
from uuid import UUID

from src.app.controllers.users.handlers import UserHandler
from src.app.middleware.middleware import auth_middleware
from src.app.services.user_service import UserService
from src.app.models.request_objects import SignupRequest, LoginRequest

def create_auth_routes(user_service: UserService) -> APIRouter:
    router = APIRouter(tags=["auth"])  # Separate router for auth routes
    user_handler = UserHandler.create(user_service)

    @router.post("/signup")
    async def signup(user: SignupRequest):
        return await user_handler.signup(user)

    @router.post("/login")
    async def login(credentials: LoginRequest):
        return await user_handler.login(credentials)

    return router

def create_user_routes(user_service: UserService) -> APIRouter:
    router = APIRouter(tags=["users"])
    user_handler = UserHandler.create(user_service)

    router.dependencies = [Depends(auth_middleware)]

    @router.get("/user/{user_id}")
    async def get_user(user_id: UUID):
        return await user_handler.get_user(str(user_id))

    @router.get("/users")
    async def get_users(request: Request):
        return await user_handler.get_users(request)

    @router.delete("/user/{user_id}")
    async def delete_user(request: Request, user_id: UUID):
        return await user_handler.delete_user(request, str(user_id))

    return router
