import pytest
from unittest.mock import Mock, MagicMock, AsyncMock
from fastapi import FastAPI, Request

from src.app.models.user import User
from src.app.models.request_objects import SignupRequest, LoginRequest
from src.app.utils.errors.error import NotExistsError, InvalidCredentialsError, UserExistsError
from src.app.config.custom_error_codes import (
    INVALID_CREDENTIALS_ERROR,
    USER_EXISTS_ERROR,
    USER_NOT_FOUND_ERROR,
    DATABASE_OPERATION_ERROR,
)
from src.app.controllers.users.handlers import UserHandler


@pytest.fixture
def app():
    """FastAPI application fixture"""
    app = FastAPI()
    return app


@pytest.fixture
def mock_request():
    """Mock FastAPI request fixture with admin role"""
    mock_req = MagicMock(spec=Request)

    # Mock request attributes
    mock_req.method = "GET"
    mock_req.url.path = "/test"
    mock_req.client.host = "127.0.0.1"
    mock_req.headers = {"content-type": "application/json"}

    class MockState:
        user = {
            "user_id": "test-user",
            "role": "admin"
        }

    mock_req.state = MockState()
    return mock_req


@pytest.fixture
def mock_user_service():
    """Mock user service fixture"""
    return Mock()


@pytest.fixture
def user_handler(mock_user_service):
    """User handler fixture with mocked service"""
    return UserHandler.create(mock_user_service)


@pytest.fixture
def sample_user():
    """Sample user fixture"""
    return User(
        name="Test User",
        email="test@watchguard.com",
        password="Hashedpassword@123",
        department="CLOUD PLATFORM",
        role="user",
        id="550e8400-e29b-41d4-a716-446655440000"
    )


@pytest.fixture
def sample_users():
    """Sample list of users fixture"""
    return [
        User(
            name="First User",
            email="first@watchguard.com",
            password="Hashedpassword@123",
            department="CLOUD PLATFORM",
            role="user",
            id="550e8400-e29b-41d4-a716-446655440000"
        ),
        User(
            name="Second User",
            email="second@watchguard.com",
            password="Hashedpassword@456",
            department="CLOUD PLATFORM",
            role="user",
            id="650e8400-e29b-41d4-a716-446655440000"
        )
    ]


class TestUserHandler:
    @pytest.mark.asyncio
    async def test_signup_success(self, user_handler, sample_user):
        signup_data = SignupRequest(
            name="Test User",
            email="test@watchguard.com",
            password="Password@123",
            department="CLOUD PLATFORM"
        )

        user_handler.user_service.signup_user.return_value = sample_user

        response = await user_handler.signup(signup_data)

        assert response["status_code"] == 200
        assert response["message"] == "User registered successfully"
        assert "token" in response["data"]
        assert response["data"]["role"] == sample_user.role

    @pytest.mark.asyncio
    async def test_signup_user_exists(self, user_handler):
        signup_data = SignupRequest(
            name="Test User",
            email="existing@watchguard.com",
            password="Password@123",
            department="CLOUD PLATFORM"
        )

        user_handler.user_service.signup_user.side_effect = UserExistsError("User already exists")

        response = await user_handler.signup(signup_data)

        assert response["status_code"] == USER_EXISTS_ERROR
        assert response["message"] == "User already exists"

    @pytest.mark.asyncio
    async def test_signup_database_error(self, user_handler):
        signup_data = SignupRequest(
            name="Test User",
            email="test@watchguard.com",
            password="Password@123",
            department="CLOUD PLATFORM"
        )

        user_handler.user_service.signup_user.side_effect = Exception("Database error")

        response = await user_handler.signup(signup_data)

        assert response["status_code"] == DATABASE_OPERATION_ERROR
        assert response["message"] == "Error creating user"

    @pytest.mark.asyncio
    async def test_login_success(self, user_handler, sample_user):
        login_data = LoginRequest(
            email="test@watchguard.com",
            password="Password@123"
        )

        user_handler.user_service.login_user.return_value = sample_user

        response = await user_handler.login(login_data)

        assert response["status_code"] == 200
        assert response["message"] == "Login successful"
        assert "token" in response["data"]
        assert response["data"]["role"] == sample_user.role
        assert response["data"]["user_id"] == sample_user.id

    @pytest.mark.asyncio
    async def test_login_invalid_credentials(self, user_handler):
        login_data = LoginRequest(
            email="test@watchguard.com",
            password="wrongpassword"
        )

        user_handler.user_service.login_user.side_effect = InvalidCredentialsError("Invalid credentials")

        response = await user_handler.login(login_data)

        assert response["status_code"] == INVALID_CREDENTIALS_ERROR
        assert response["message"] == "Invalid credentials"

    @pytest.mark.asyncio
    async def test_get_user_success(self, user_handler, sample_user):
        user_id = "550e8400-e29b-41d4-a716-446655440000"
        user_handler.user_service.get_user_by_id.return_value = sample_user

        response = await user_handler.get_user(user_id)

        assert response["status_code"] == 200
        assert response["message"] == "User fetched successfully"
        assert response["data"]["email"] == sample_user.email
        assert response["data"]["name"] == sample_user.name

    @pytest.mark.asyncio
    async def test_get_user_not_found(self, user_handler):
        user_id = "550e8400-e29b-41d4-a716-446655440000"
        user_handler.user_service.get_user_by_id.side_effect = NotExistsError("User not found")

        response = await user_handler.get_user(user_id)

        assert response["status_code"] == USER_NOT_FOUND_ERROR
        assert response["message"] == "User not found"

    @pytest.mark.asyncio
    async def test_get_users_success(self, user_handler, mock_request, sample_users):
        user_handler.user_service.get_users.return_value = sample_users

        response = await user_handler.get_users(mock_request)

        assert response["status_code"] == 200
        assert response["message"] == "Users fetched successfully"
        assert len(response["data"]) == 2
        assert response["data"][0]["email"] == "first@watchguard.com"
        assert response["data"][1]["email"] == "second@watchguard.com"

    @pytest.mark.asyncio
    async def test_get_users_database_error(self, user_handler, mock_request):
        user_handler.user_service.get_users.side_effect = Exception("Database error")

        response = await user_handler.get_users(mock_request)

        assert response["status_code"] == DATABASE_OPERATION_ERROR
        assert response["message"] == "Error fetching users"

    @pytest.mark.asyncio
    async def test_delete_user_success(self, user_handler, mock_request):
        user_id = "550e8400-e29b-41d4-a716-446655440000"

        response = await user_handler.delete_user(mock_request, user_id)

        assert response["status_code"] == 200
        assert response["message"] == "User deleted successfully"
        user_handler.user_service.delete_user_account.assert_awaited_once_with(user_id)

    @pytest.mark.asyncio
    async def test_delete_user_not_found(self, user_handler, mock_request):
        user_id = "550e8400-e29b-41d4-a716-446655440000"
        user_handler.user_service.delete_user_account.side_effect = NotExistsError("User not found")

        response = await user_handler.delete_user(mock_request, user_id)

        assert response["status_code"] == USER_NOT_FOUND_ERROR
        assert response["message"] == "User not found"