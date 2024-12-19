from fastapi import APIRouter, Depends, Path, Query
from typing import Optional
from uuid import UUID

from src.app.controllers.users.handlers import UserHandler
from src.app.middleware.middleware import auth_middleware
from src.app.services.user_service import UserService
from src.app.models.request_objects import SignupRequest, LoginRequest

def create_user_routes(user_service: UserService) -> APIRouter:
    router = APIRouter(prefix="/users", tags=["users"])
    user_handler = UserHandler.create(user_service)

    @router.post(
        "/signup",
        response_model=dict,
        summary="Register a new user",
        description="Create a new user account"
    )
    async def signup(user: SignupRequest):
        return await user_handler.signup(user)

    @router.post(
        "/login",
        response_model=dict,
        summary="User login",
        description="Authenticate user and return access token"
    )
    async def login(credentials: LoginRequest):
        return await user_handler.login(credentials)

    @router.get(
        "/{user_id}",
        response_model=dict,
        summary="Get user details",
        description="Get detailed information about a specific user"
    )
    async def get_user(
        user_id: UUID = Path(..., description="The ID of the user to retrieve"),
        _: dict = Depends(auth_middleware)
    ):
        return await user_handler.get_user(str(user_id))

    @router.get(
        "/",
        response_model=dict,
        summary="Get all users",
        description="Get a list of all users. Requires admin access."
    )
    async def get_users(
        department: Optional[str] = Query(None, description="Filter users by department"),
        _: dict = Depends(auth_middleware)
    ):
        return await user_handler.get_users(department)

    @router.delete(
        "/{user_id}",
        response_model=dict,
        summary="Delete user",
        description="Delete a user account. Requires admin access."
    )
    async def delete_user(
        user_id: UUID = Path(..., description="The ID of the user to delete"),
        _: dict = Depends(auth_middleware)
    ):
        return await user_handler.delete_user(str(user_id))

    return router
