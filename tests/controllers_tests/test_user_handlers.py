import unittest
from unittest.mock import Mock, patch
from flask import Flask, request
import json

from src.app.controllers.users.handlers import UserHandler
from src.app.models.user import User
from src.app.services.user_service import UserService
from src.app.utils.errors.error import (
    UserExistsError,
    InvalidCredentialsError,
    MissingFieldError,
    DatabaseError
)
from werkzeug.routing import ValidationError


class TestUserHandler(unittest.TestCase):
    def setUp(self):
        # Create a Flask test client
        self.app = Flask(__name__)
        self.app_context = self.app.app_context()
        self.app_context.push()

        # Mock UserService
        self.mock_user_service = Mock(spec=UserService)

        # Create UserHandler with mock service
        self.user_handler = UserHandler.create(self.mock_user_service)

    def tearDown(self):
        # Pop the application context
        self.app_context.pop()

    def test_login_successful(self):
        """
        Test successful login
        """
        # Prepare test data
        login_data = {
            'email': 'test@example.com',
            'password': 'password123'
        }

        # Mock user for successful login
        mock_user = User(
            id='123',
            email='test@example.com',
            name='Test User',
            role='user'
        )

        # Setup mock service method
        self.mock_user_service.login_user.return_value = mock_user

        # Simulate request
        with self.app.test_request_context(
                json=login_data,
                method='POST'
        ):
            response, status_code = self.user_handler.login()

        # Assertions
        self.assertEqual(status_code, 200)
        self.assertEqual(response['message'], 'Login successful')
        self.assertIn('token', response['data'])
        self.assertEqual(response['data']['role'], 'user')
        self.assertEqual(response['data']['user_id'], '123')

    def test_login_invalid_credentials(self):
        """
        Test login with invalid credentials
        """
        # Prepare test data
        login_data = {
            'email': 'test@example.com',
            'password': 'wrongpassword'
        }

        # Setup mock service to raise InvalidCredentialsError
        self.mock_user_service.login_user.side_effect = InvalidCredentialsError("Invalid credentials")

        # Simulate request
        with self.app.test_request_context(
                json=login_data,
                method='POST'
        ):
            response, status_code = self.user_handler.login()

        # Assertions
        self.assertEqual(status_code, 400)
        self.assertEqual(response['message'], 'Invalid email or password')

    def test_signup_successful(self):
        """
        Test successful user signup
        """
        # Prepare test data
        signup_data = {
            'name': 'Test User',
            'email': 'test@example.com',
            'password': 'password123',
            'department': 'IT'
        }

        # Simulate request
        with self.app.test_request_context(
                json=signup_data,
                method='POST'
        ):
            response, status_code = self.user_handler.signup()

        # Assertions
        self.assertEqual(status_code, 200)
        self.assertEqual(response['message'], 'User registered successfully')
        self.assertIn('token', response['data'])
        self.assertIn('role', response['data'])
        self.assertIn('user_id', response['data'])

    def test_signup_user_exists(self):
        """
        Test signup when user already exists
        """
        # Prepare test data
        signup_data = {
            'name': 'Test User',
            'email': 'test@example.com',
            'password': 'password123',
            'department': 'IT'
        }

        # Setup mock service to raise UserExistsError
        self.mock_user_service.signup_user.side_effect = UserExistsError("User already exists")

        # Simulate request
        with self.app.test_request_context(
                json=signup_data,
                method='POST'
        ):
            response, status_code = self.user_handler.signup()

        # Assertions
        self.assertEqual(status_code, 409)
        self.assertEqual(response['message'], 'User already exists')

    def test_get_users_successful(self):
        """
        Test fetching users successfully
        """
        # Create mock users
        mock_users = [
            User(id='1', name='User 1', email='user1@example.com'),
            User(id='2', name='User 2', email='user2@example.com')
        ]

        # Setup mock service
        self.mock_user_service.get_users.return_value = mock_users

        # Simulate request context (for admin decorator)
        with patch('src.app.utils.utils.g') as mock_g:
            mock_g.role = 'admin'
            response, status_code = self.user_handler.get_users()

        # Assertions
        self.assertEqual(status_code, 200)
        self.assertEqual(response['message'], 'Users fetched successfully')
        self.assertEqual(len(response['data']), 2)

    def test_get_user_successful(self):
        """
        Test fetching a single user successfully
        """
        # Create mock user
        mock_user = User(
            id='123',
            name='Test User',
            email='test@example.com'
        )

        # Setup mock service
        self.mock_user_service.get_user_by_id.return_value = mock_user

        # Simulate request
        response, status_code = self.user_handler.get_user('123')

        # Assertions
        self.assertEqual(status_code, 200)
        self.assertEqual(response['message'], 'User details retrieved successfully')
        self.assertEqual(response['data']['id'], '123')

    def test_delete_user_successful(self):
        """
        Test successful user deletion
        """
        # Setup mock service
        self.mock_user_service.delete_user_account.return_value = True

        # Simulate request context (for admin decorator)
        with patch('src.app.utils.utils.g') as mock_g:
            mock_g.role = 'admin'
            response, status_code = self.user_handler.delete_user('123')

        # Assertions
        self.assertEqual(status_code, 200)
        self.assertEqual(response['message'], 'User account deleted successfully')

    def test_delete_user_not_found(self):
        """
        Test user deletion when user is not found
        """
        # Setup mock service
        self.mock_user_service.delete_user_account.return_value = False

        # Simulate request context (for admin decorator)
        with patch('src.app.utils.utils.g') as mock_g:
            mock_g.role = 'admin'
            response, status_code = self.user_handler.delete_user('123')

        # Assertions
        self.assertEqual(status_code, 404)
        self.assertEqual(response['message'], 'User not found')


if __name__ == '__main__':
    unittest.main()