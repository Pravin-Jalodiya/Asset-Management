import unittest
import jwt
from unittest.mock import patch
from flask import Flask, g

from src.app.utils.utils import Utils
from src.app.config.types import Role


class TestUtils(unittest.TestCase):
    def setUp(self):
        # Setup method to run before each tests
        pass

    def test_hash_password_unique(self):
        """
        Test that hashing the same password twice produces different hashes
        """
        password = "mypassword"
        hashed_password1 = Utils.hash_password(password)
        hashed_password2 = Utils.hash_password(password)

        # Different hashes for same password
        self.assertNotEqual(hashed_password1, hashed_password2)

        # Ensure both start with bcrypt hash prefix
        self.assertTrue(hashed_password1.startswith("$2b$"))
        self.assertTrue(hashed_password2.startswith("$2b$"))

    def test_check_password_success(self):
        """
        Test password verification with correct password
        """
        password = "mypassword"
        hashed_password = Utils.hash_password(password)

        # Correct password should return True
        self.assertTrue(Utils.check_password(password, hashed_password))

    def test_check_password_failure(self):
        """
        Test password verification with incorrect password
        """
        password = "mypassword"
        wrong_password = "wrongpassword"
        hashed_password = Utils.hash_password(password)

        # Wrong password should return False
        self.assertFalse(Utils.check_password(wrong_password, hashed_password))

    def test_create_jwt_token_success(self):
        """
        Test JWT token creation with valid inputs
        """
        user_id = "12345"
        role = "admin"

        token = Utils.create_jwt_token(user_id, role)

        # Assert token is a string
        self.assertIsInstance(token, str)

        # Decode the token to verify contents
        decoded_payload = jwt.decode(token, Utils.SECRET_KEY, algorithms=["HS256"])

        # Verify payload contents
        self.assertEqual(decoded_payload["user_id"], user_id)
        self.assertEqual(decoded_payload["role"], role)

        # Check token expiration fields
        self.assertIn("exp", decoded_payload)
        self.assertIn("iat", decoded_payload)
        self.assertIn("nbf", decoded_payload)

    def test_decode_jwt_token_success(self):
        """
        Test JWT token decoding
        """
        user_id = "12345"
        role = "admin"

        token = Utils.create_jwt_token(user_id, role)
        decoded_payload = Utils.decode_jwt_token(token)

        # Verify decoded payload
        self.assertEqual(decoded_payload["user_id"], user_id)
        self.assertEqual(decoded_payload["role"], role)

    def test_decode_jwt_token_expired(self):
        """
        Test decoding an expired JWT token
        """
        # Create a token that's already expired
        with patch('jwt.decode') as mock_decode:
            mock_decode.side_effect = jwt.ExpiredSignatureError("Token expired")

            with self.assertRaises(jwt.ExpiredSignatureError):
                # Create a token and then try to decode it as if it's expired
                token = "some.expired.token"
                Utils.decode_jwt_token(token)

    def test_decode_jwt_token_invalid(self):
        """
        Test decoding an invalid JWT token
        """
        with self.assertRaises(jwt.InvalidTokenError):
            Utils.decode_jwt_token("invalid.token")

    def test_admin_decorator_authorized(self):
        """
        Test admin decorator with authorized access
        """
        # Create a Flask app context for testing
        app = Flask(__name__)
        with app.app_context():
            # Set up g with admin role
            g.role = Role.ADMIN.value

            # Mock function to be decorated
            @Utils.admin
            def test_function():
                return "Authorized"

            # Call the decorated function
            result = test_function()
            self.assertEqual(result, "Authorized")

    def test_admin_decorator_unauthorized(self):
        """
        Test admin decorator with unauthorized access
        """
        # Create a Flask app context for testing
        app = Flask(__name__)
        with app.app_context():
            # Set up g with non-admin role
            g.role = Role.USER.value

            # Mock function to be decorated
            @Utils.admin
            def test_function():
                return "Authorized"

            # Call the decorated function
            result = test_function()

            # Check for unauthorized response
            self.assertEqual(result[1], 403)
            self.assertIn("Unauthorized", result[0].get_json()["message"])

    def test_create_jwt_token_exception(self):
        """
        Test JWT token creation with problematic inputs
        """
        with patch('jwt.encode') as mock_encode:
            mock_encode.side_effect = Exception("Encoding error")

            with self.assertRaises(ValueError):
                Utils.create_jwt_token("user_id", "role")
