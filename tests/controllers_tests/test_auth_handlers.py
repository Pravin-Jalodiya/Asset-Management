import pytest
from unittest.mock import Mock, MagicMock, AsyncMock
from fastapi import FastAPI, Request

from src.app.controllers.auth.handlers import AuthHandler
from src.app.models.user import User
from src.app.models.request_objects import SignupRequest, LoginRequest
from src.app.utils.errors.error import InvalidCredentialsError, UserExistsError
from src.app.config.custom_error_codes import ErrorCodes


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
def auth_handler(mock_user_service):
    """User handler fixture with mocked service"""
    return AuthHandler.create(mock_user_service)


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


class TestAuthHandler:
    @pytest.mark.asyncio
    async def test_signup_success(self, auth_handler, sample_user):
        signup_data = SignupRequest(
            name="Test User",
            email="test@watchguard.com",
            password="Password@123",
            department="CLOUD PLATFORM"
        )

        auth_handler.user_service.signup_user.return_value = sample_user

        response = await auth_handler.signup(signup_data)

        assert response["status_code"] == 200
        assert response["message"] == "User registered successfully"
        assert "token" in response["data"]
        assert response["data"]["role"] == sample_user.role

    @pytest.mark.asyncio
    async def test_signup_user_exists(self, auth_handler):
        signup_data = SignupRequest(
            name="Test User",
            email="existing@watchguard.com",
            password="Password@123",
            department="CLOUD PLATFORM"
        )

        auth_handler.user_service.signup_user.side_effect = UserExistsError("User already exists")

        response = await auth_handler.signup(signup_data)

        assert response["status_code"] == ErrorCodes.USER_EXISTS_ERROR.value
        assert response["message"] == "User already exists"

    @pytest.mark.asyncio
    async def test_signup_database_error(self, auth_handler):
        signup_data = SignupRequest(
            name="Test User",
            email="test@watchguard.com",
            password="Password@123",
            department="CLOUD PLATFORM"
        )

        auth_handler.user_service.signup_user.side_effect = Exception("Database error")

        response = await auth_handler.signup(signup_data)
        response_body = response.body.decode()  # Convert bytes to string
        import json
        response_data = json.loads(response_body)  # Parse JSON string

        assert response.status_code == 500  # HTTP status code
        assert response_data["status_code"] == ErrorCodes.DATABASE_OPERATION_ERROR.value  # Custom status code
        assert response_data["message"] == "Error creating user"

    @pytest.mark.asyncio
    async def test_login_success(self, auth_handler, sample_user):
        login_data = LoginRequest(
            email="test@watchguard.com",
            password="Password@123"
        )

        auth_handler.user_service.login_user.return_value = sample_user

        response = await auth_handler.login(login_data)

        assert response["status_code"] == 200
        assert response["message"] == "Login successful"
        assert "token" in response["data"]
        assert response["data"]["role"] == sample_user.role
        assert response["data"]["user_id"] == sample_user.id

    @pytest.mark.asyncio
    async def test_login_invalid_credentials(self, auth_handler):
        login_data = LoginRequest(
            email="test@watchguard.com",
            password="wrongpassword"
        )

        auth_handler.user_service.login_user.side_effect = InvalidCredentialsError("Invalid credentials")

        response = await auth_handler.login(login_data)

        assert response["status_code"] == ErrorCodes.INVALID_CREDENTIALS_ERROR.value
        assert response["message"] == "Invalid credentials"
