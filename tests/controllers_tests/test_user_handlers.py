import uuid
import pytest
from unittest.mock import Mock
from flask import Flask, g

from src.app.config.custom_error_codes import (
    VALIDATION_ERROR,
    MISSING_FIELD_ERROR,
    INVALID_CREDENTIALS_ERROR,
    USER_EXISTS_ERROR,
    DATABASE_OPERATION_ERROR,
    USER_NOT_FOUND_ERROR,
    RECORD_NOT_FOUND_ERROR
)
from src.app.models.user import User
from src.app.utils.errors.error import (
    UserExistsError,
    InvalidCredentialsError,
    MissingFieldError,
    DatabaseError
)
from src.app.controllers.users.handlers import UserHandler

@pytest.fixture
def app():
    """Flask application fixture"""
    app = Flask(__name__)
    return app

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
        id=str(uuid.uuid4()),
        name="Test User",
        email="test@example.com",
        password="hashed_password",
        department="IT",
        role="user"
    )

@pytest.fixture
def sample_users():
    """Sample list of users fixture"""
    return [
        User(
            id=str(uuid.uuid4()),
            name="User One",
            email="user1@example.com",
            password="hashed_password1",
            department="IT",
            role="user"
        ),
        User(
            id=str(uuid.uuid4()),
            name="User Two",
            email="user2@example.com",
            password="hashed_password2",
            department="HR",
            role="admin"
        )
    ]

class TestUserHandler:
    def test_login_success(self, app, user_handler, sample_user):
        """Test successful login"""
        login_data = {
            "email": "test@watchguard.com",
            "password": "password123"
        }
        user_handler.user_service.login_user.return_value = sample_user

        with app.test_request_context(json=login_data):
            response, status_code = user_handler.login()

        assert status_code == 200
        assert response["status_code"] == 200
        assert response["message"] == "Login successful"
        assert "token" in response["data"]
        assert response["data"]["role"] == sample_user.role
        assert response["data"]["user_id"] == sample_user.id

    def test_login_validation_error(self, app, user_handler):
        """Test login with validation error"""
        login_data = {
            "email": "invalid-email",
            "password": "pass"
        }

        with app.test_request_context(json=login_data):
            response, status_code = user_handler.login()

        assert status_code == 400
        assert response["status_code"] == VALIDATION_ERROR

    def test_login_missing_field(self, app, user_handler):
        """Test login with missing field"""
        login_data = {
            "email": "test@example.com"
        }
        user_handler.user_service.login_user.side_effect = MissingFieldError("Password is required")

        with app.test_request_context(json=login_data):
            response, status_code = user_handler.login()

        assert status_code == 400
        assert response["status_code"] == MISSING_FIELD_ERROR

    def test_login_invalid_credentials(self, app, user_handler):
        """Test login with invalid credentials"""
        login_data = {
            "email": "test@watchguard.com",
            "password": "wrongpass"
        }
        user_handler.user_service.login_user.side_effect = InvalidCredentialsError("Invalid email or password")

        with app.test_request_context(json=login_data):
            response, status_code = user_handler.login()

        assert status_code == 400
        assert response["status_code"] == INVALID_CREDENTIALS_ERROR
        assert response["message"] == "Invalid email or password"

    def test_signup_success(self, app, user_handler, sample_user):
        """Test successful signup"""
        signup_data = {
            "name": "Test User",
            "email": "test@watchguard.com",
            "password": "Password@123",
            "department": "CLOUD PLATFORM"
        }
        user_handler.user_service.signup_user.return_value = None

        with app.test_request_context(json=signup_data):
            response, status_code = user_handler.signup()

        assert status_code == 200
        assert response["status_code"] == 200
        assert response["message"] == "User registered successfully"
        assert "token" in response["data"]

    def test_signup_user_exists(self, app, user_handler):
        """Test signup with existing user"""
        signup_data = {
            "name": "Test User",
            "email": "existing@watchguard.com",
            "password": "Password@123",
            "department": "CLOUD PLATFORM"
        }
        user_handler.user_service.signup_user.side_effect = UserExistsError("User already exists")

        with app.test_request_context(json=signup_data):
            response, status_code = user_handler.signup()

        assert status_code == 409
        assert response["status_code"] == USER_EXISTS_ERROR

    def test_get_users_success(self, app, user_handler, sample_users):
        """Test successful retrieval of all users"""
        user_handler.user_service.get_users.return_value = sample_users

        with app.test_request_context():
            g.role = 'admin'
            response, status_code = user_handler.get_users()

        assert status_code == 200
        assert response["status_code"] == 200
        assert response["message"] == "Users fetched successfully"
        assert len(response["data"]) == 2

    def test_get_users_database_error(self, app, user_handler):
        """Test get users with database error"""
        user_handler.user_service.get_users.side_effect = DatabaseError("Database error")

        with app.test_request_context():
            g.role = 'admin'
            response, status_code = user_handler.get_users()

        assert status_code == 500
        assert response["status_code"] == DATABASE_OPERATION_ERROR
        assert response["message"] == "Error fetching users"

    def test_get_user_success(self, app, user_handler, sample_user):
        """Test successful retrieval of single user"""
        user_id = str(uuid.uuid4())
        user_handler.user_service.get_user_by_id.return_value = sample_user

        with app.test_request_context():
            response, status_code = user_handler.get_user(user_id)

        assert status_code == 200
        assert response["status_code"] == 200
        assert response["message"] == "User details retrieved successfully"
        assert response["data"]["email"] == sample_user.email

    def test_get_user_not_found(self, app, user_handler):
        """Test get user with non-existent user"""
        user_id = str(uuid.uuid4())
        user_handler.user_service.get_user_by_id.side_effect = DatabaseError("Error fetching user")

        with app.test_request_context():
            response, status_code = user_handler.get_user(user_id)

        assert status_code == 500
        assert response["status_code"] == DATABASE_OPERATION_ERROR
        assert response["message"] == "Error fetching user details"

    def test_delete_user_success(self, app, user_handler):
        """Test successful user deletion"""
        user_id = str(uuid.uuid4())
        user_handler.user_service.delete_user_account.return_value = True

        with app.test_request_context():
            g.role = 'admin'
            response, status_code = user_handler.delete_user(user_id)

        assert status_code == 200
        assert response["status_code"] == 200
        assert response["message"] == "User account deleted successfully"

    def test_delete_user_invalid_uuid(self, app, user_handler):
        """Test delete user with invalid UUID"""
        invalid_user_id = "invalid-uuid"

        with app.test_request_context():
            g.role = 'admin'
            response, status_code = user_handler.delete_user(invalid_user_id)

        assert status_code == 200
        assert response["status_code"] == 200
        assert response["message"] == "Invalid user id"

    def test_delete_user_not_found(self, app, user_handler):
        """Test delete non-existent user"""
        user_id = str(uuid.uuid4())
        user_handler.user_service.delete_user_account.return_value = False

        with app.test_request_context():
            g.role = 'admin'
            response, status_code = user_handler.delete_user(user_id)

        assert status_code == 404
        assert response["status_code"] == USER_NOT_FOUND_ERROR
        assert response["message"] == "User not found"