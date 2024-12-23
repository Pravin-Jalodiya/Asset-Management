from fastapi import APIRouter

from src.app.controllers.auth.handlers import AuthHandler
from src.app.models.request_objects import SignupRequest, LoginRequest
from src.app.services.user_service import UserService


def create_auth_routes(user_service: UserService) -> APIRouter:
    router = APIRouter(tags=["auth"])  # Separate router for auth routes
    auth_handler = AuthHandler.create(user_service)

    @router.post("/signup")
    async def signup(user: SignupRequest):
        return await auth_handler.signup(user)

    @router.post("/login")
    async def login(credentials: LoginRequest):
        return await auth_handler.login(credentials)

    return router
