import unittest
from unittest.mock import MagicMock, patch
import uuid
from src.app.models.user import User, UserDTO
from src.app.services.user_service import UserService
from src.app.utils.errors.error import (
    UserExistsError,
    InvalidCredentialsError, NotExistsError
)
from src.app.utils.utils import Utils


class TestUserService(unittest.TestCase):
    def setUp(self):
        # Create a mock user repository for testing
        self.mock_user_repository = MagicMock()
        self.user_service = UserService(self.mock_user_repository)

    def test_signup_user_successful(self):
        """
        Test successful user signup
        """
        # Arrange
        new_user = User(
            name="New User",
            email="newuser@example.com",
            password="password123",
            department="IT"
        )
        # Simulate that no existing user is found with this email
        self.mock_user_repository.fetch_user_by_email.return_value = None

        # Act
        with patch('src.app.utils.utils.Utils.hash_password', return_value='hashed_password'):
            self.user_service.signup_user(new_user)

        # Assert
        # Verify the email was checked for existing user
        self.mock_user_repository.fetch_user_by_email.assert_called_once_with(new_user.email)

        # Verify the password was hashed
        self.assertEqual(new_user.password, 'hashed_password')

        # Verify the user was saved to the repository
        self.mock_user_repository.save_user.assert_called_once_with(new_user)

    def test_signup_user_raises_user_exists_error(self):
        """
        Test signup fails when user with email already exists
        """
        # Arrange
        existing_user = User(
            name="Existing User",
            email="existing@example.com",
            password="password123",
            department="HR"
        )
        # Simulate an existing user with this email
        self.mock_user_repository.fetch_user_by_email.return_value = existing_user

        # Act & Assert
        with self.assertRaises(UserExistsError) as context:
            self.user_service.signup_user(existing_user)

        # Verify the error message
        self.assertEqual(str(context.exception), "User with this email already exists")

        # Verify save_user was not called
        self.mock_user_repository.save_user.assert_not_called()

    def test_login_user_successful(self):
        """
        Test successful user login
        """
        # Arrange
        email = "user@example.com"
        password = "password123"
        existing_user = User(
            name="Test User",
            email=email,
            password=Utils.hash_password(password),
            department="Engineering"
        )

        # Simulate finding the user and password check
        self.mock_user_repository.fetch_user_by_email.return_value = existing_user

        with patch('src.app.utils.utils.Utils.check_password', return_value=True):
            # Act
            logged_in_user = self.user_service.login_user(email, password)

        # Assert
        self.assertEqual(logged_in_user, existing_user)
        self.mock_user_repository.fetch_user_by_email.assert_called_once_with(email)

    def test_login_user_raises_invalid_credentials(self):
        """
        Test login fails with incorrect credentials
        """
        # Arrange
        email = "user@example.com"
        password = "wrongpassword"

        # Simulate no user found or incorrect password
        self.mock_user_repository.fetch_user_by_email.return_value = None

        # Act & Assert
        with self.assertRaises(InvalidCredentialsError) as context:
            self.user_service.login_user(email, password)

        self.assertEqual(str(context.exception), "Email or password incorrect")

    def test_delete_user_account_successful(self):
        """
        Test successful user account deletion
        """
        # Arrange
        user_id = str(uuid.uuid4())
        existing_user = User(
            name="Test User",
            email="user@example.com",
            department="Sales",
            id=user_id,
            password="password"
        )

        # Simulate finding the user
        self.mock_user_repository.fetch_user_by_id.return_value = existing_user
        self.mock_user_repository.delete_user.return_value = True

        # Act
        result = self.user_service.delete_user_account(user_id)

        # Assert
        self.assertTrue(result)
        self.mock_user_repository.fetch_user_by_id.assert_called_once_with(user_id)
        self.mock_user_repository.delete_user.assert_called_once_with(user_id)

    def test_delete_user_account_nonexistent_user(self):
        """
        Test delete user account for non-existent user
        """
        # Arrange
        user_id = str(uuid.uuid4())

        # Simulate no user found
        self.mock_user_repository.fetch_user_by_id.return_value = None

        # Act & Assert
        with self.assertRaises(NotExistsError) as context:
            self.user_service.delete_user_account(user_id)

        self.assertEqual(str(context.exception), "User does not exist")
        self.mock_user_repository.fetch_user_by_id.assert_called_once_with(user_id)
        self.mock_user_repository.delete_user.assert_not_called()

    def test_get_users_returns_list(self):
        """
        Test get_users returns a list of users
        """
        # Arrange
        expected_users = [
            UserDTO(
                id=str(uuid.uuid4()),
                name="User One",
                email="user1@example.com",
                department="IT"
            ),
            UserDTO(
                id=str(uuid.uuid4()),
                name="User Two",
                email="user2@example.com",
                department="HR"
            )
        ]
        self.mock_user_repository.fetch_users.return_value = expected_users

        # Act
        result = self.user_service.get_users()

        # Assert
        self.assertEqual(result, expected_users)
        self.mock_user_repository.fetch_users.assert_called_once()

    def test_get_users_returns_empty_list(self):
        """
        Test get_users returns an empty list when no users found
        """
        # Arrange
        self.mock_user_repository.fetch_users.return_value = None

        # Act
        result = self.user_service.get_users()

        # Assert
        self.assertEqual(result, [])
        self.mock_user_repository.fetch_users.assert_called_once()

    def test_get_user_by_id_successful(self):
        """
        Test get_user_by_id returns user when found
        """
        # Arrange
        user_id = str(uuid.uuid4())
        expected_user = User(
            id=user_id,
            name="Test User",
            email="user@example.com",
            department="Engineering",
            password="hashed_password"
        )
        self.mock_user_repository.fetch_user_by_id.return_value = expected_user

        # Act
        result = self.user_service.get_user_by_id(user_id)

        # Assert
        self.assertEqual(result, expected_user)
        self.mock_user_repository.fetch_user_by_id.assert_called_once_with(user_id)

    def test_get_user_by_id_returns_none(self):
        """
        Test get_user_by_id returns None when no user found
        """
        # Arrange
        user_id = str(uuid.uuid4())
        self.mock_user_repository.fetch_user_by_id.return_value = None

        # Act
        result = self.user_service.get_user_by_id(user_id)

        # Assert
        self.assertIsNone(result)
        self.mock_user_repository.fetch_user_by_id.assert_called_once_with(user_id)

    def test_get_user_by_email_successful(self):
        """
        Test get_user_by_email returns user when found
        """
        # Arrange
        email = "user@example.com"
        expected_user = User(
            name="Test User",
            email=email,
            department="Marketing",
            id=str(uuid.uuid4()),
            password="hashed_password"
        )
        self.mock_user_repository.fetch_user_by_email.return_value = expected_user

        # Act
        result = self.user_service.get_user_by_email(email)

        # Assert
        self.assertEqual(result, expected_user)
        self.mock_user_repository.fetch_user_by_email.assert_called_once_with(email)

    def test_get_user_by_email_returns_none(self):
        """
        Test get_user_by_email returns None when no user found
        """
        # Arrange
        email = "nonexistent@example.com"
        self.mock_user_repository.fetch_user_by_email.return_value = None

        # Act
        result = self.user_service.get_user_by_email(email)

        # Assert
        self.assertIsNone(result)
        self.mock_user_repository.fetch_user_by_email.assert_called_once_with(email)
