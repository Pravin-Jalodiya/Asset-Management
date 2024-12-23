import pytest
from unittest.mock import Mock, MagicMock, AsyncMock
from fastapi import FastAPI, Request

from src.app.models.user import User
from src.app.utils.errors.error import NotExistsError
from src.app.config.custom_error_codes import ErrorCodes
from src.app.controllers.users.handlers import UserHandler
from src.app.utils.context import get_user_from_context, set_user_to_context


@pytest.fixture
def app():
    """FastAPI application fixture"""
    app = FastAPI()
    return app


@pytest.fixture
def mock_request():
    """Mock FastAPI request fixture with admin role"""
    # Create base mock request with receive channel
    mock_scope = {
        "type": "http",
        "headers": [],
        "method": "GET",
        "path": "/",
        "query_string": b"",
        "client": ("127.0.0.1", 8000),
    }

    async def mock_receive():
        return {"type": "http.request", "body": b""}

    mock_request = Request(mock_scope, receive=mock_receive)
    
    # Set up admin user directly on state
    mock_request.state.user = {"role": "admin", "user_id": "test-user"}
    
    return mock_request


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
    def setup_method(self):
        """Setup method that runs before each test"""
        # Patch the get_user_from_context function
        self.original_get_user = get_user_from_context
        get_user_from_context.__code__ = (lambda r: r.state.user).__code__

    def teardown_method(self):
        """Teardown method that runs after each test"""
        # Restore the original function
        get_user_from_context.__code__ = self.original_get_user.__code__

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

        assert response["status_code"] == ErrorCodes.USER_NOT_FOUND_ERROR.value
        assert response["message"] == "User not found"

    @pytest.mark.asyncio
    async def test_get_users_success(self, user_handler, mock_request, sample_users):
        # Verify admin context is set
        assert mock_request.state.user["role"] == "admin"
        
        user_handler.user_service.get_users.return_value = sample_users

        response = await user_handler.get_users(mock_request)

        assert response["status_code"] == 200
        assert response["message"] == "Users fetched successfully"
        assert len(response["data"]) == 2
        assert response["data"][0]["email"] == "first@watchguard.com"
        assert response["data"][1]["email"] == "second@watchguard.com"

    @pytest.mark.asyncio
    async def test_get_users_database_error(self, user_handler, mock_request):
        # Verify the mock request has proper admin privileges
        assert mock_request.state.user["role"] == "admin"

        user_handler.user_service.get_users.side_effect = Exception("Database error")

        response = await user_handler.get_users(mock_request)

        # Handle both JSONResponse and dict responses
        if hasattr(response, 'body'):
            # If it's a JSONResponse
            response_body = response.body.decode()
            import json
            response_data = json.loads(response_body)
            assert response.status_code == 500
        else:
            # If it's a dict
            response_data = response

        assert response_data["status_code"] == ErrorCodes.DATABASE_OPERATION_ERROR.value
        assert response_data["message"] == "Error fetching users"

    @pytest.mark.asyncio
    async def test_delete_user_success(self, user_handler, mock_request):
        user_id = "550e8400-e29b-41d4-a716-446655440000"

        response = await user_handler.delete_user(mock_request, user_id)

        assert response["status_code"] == 200
        assert response["message"] == "User deleted successfully"
        user_handler.user_service.delete_user_account.assert_called_once_with(user_id)

    @pytest.mark.asyncio
    async def test_delete_user_not_found(self, user_handler, mock_request):
        user_id = "550e8400-e29b-41d4-a716-446655440000"
        user_handler.user_service.delete_user_account.side_effect = NotExistsError("User not found")

        response = await user_handler.delete_user(mock_request, user_id)

        assert response["status_code"] == ErrorCodes.USER_NOT_FOUND_ERROR.value
        assert response["message"] == "User not found"
