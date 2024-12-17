import unittest
from unittest.mock import patch
from flask import Flask, g
import jwt
from src.app.middleware.middleware import auth_middleware
from src.app.config.custom_error_codes import (
    INVALID_TOKEN_ERROR,
    INVALID_TOKEN_PAYLOAD_ERROR,
    EXPIRED_TOKEN_ERROR
)

# Set up a Flask app for testing
app = Flask(__name__)

class TestAuthMiddleware(unittest.TestCase):

    def setUp(self):
        app.config['TESTING'] = True
        self.app = app.test_client()

    @patch('src.app.utils.utils.Utils.decode_jwt_token')
    def test_no_authorization_header(self, mock_decode):
        with app.test_request_context('/some/protected/route'):
            response, status_code = auth_middleware()
            self.assertEqual(status_code, 401)
            self.assertEqual(response['status_code'], INVALID_TOKEN_ERROR)
            self.assertEqual(response['message'], "Unauthorized, missing or invalid token")

    @patch('src.app.utils.utils.Utils.decode_jwt_token')
    def test_invalid_authorization_format(self, mock_decode):
        with app.test_request_context(
            '/some/protected/route', headers={'Authorization': 'InvalidToken'}
        ):
            response, status_code = auth_middleware()
            self.assertEqual(status_code, 401)
            self.assertEqual(response['status_code'], INVALID_TOKEN_ERROR)
            self.assertEqual(response['message'], "Unauthorized, missing or invalid token")

    @patch('src.app.utils.utils.Utils.decode_jwt_token')
    def test_expired_token(self, mock_decode):
        mock_decode.side_effect = jwt.ExpiredSignatureError
        with app.test_request_context(
            '/some/protected/route', headers={'Authorization': 'Bearer expired.token.here'}
        ):
            response, status_code = auth_middleware()
            self.assertEqual(status_code, 401)
            self.assertEqual(response['status_code'], EXPIRED_TOKEN_ERROR)
            self.assertEqual(response['message'], "Unauthorized, token has expired")

    @patch('src.app.utils.utils.Utils.decode_jwt_token')
    def test_invalid_token(self, mock_decode):
        mock_decode.side_effect = jwt.InvalidTokenError
        with app.test_request_context(
            '/some/protected/route', headers={'Authorization': 'Bearer invalid.token.here'}
        ):
            response, status_code = auth_middleware()
            self.assertEqual(status_code, 401)
            self.assertEqual(response['status_code'], INVALID_TOKEN_ERROR)
            self.assertEqual(response['message'], "Unauthorized, missing or invalid token")

    @patch('src.app.utils.utils.Utils.decode_jwt_token')
    def test_invalid_token_payload(self, mock_decode):
        mock_decode.return_value = {"invalid_key": "value"}
        with app.test_request_context(
            '/some/protected/route', headers={'Authorization': 'Bearer valid.token.here'}
        ):
            response, status_code = auth_middleware()
            self.assertEqual(status_code, 401)
            self.assertEqual(response['status_code'], INVALID_TOKEN_PAYLOAD_ERROR)
            self.assertEqual(response['message'], "Unauthorized, invalid token payload")

    @patch('src.app.utils.utils.Utils.decode_jwt_token')
    def test_valid_token(self, mock_decode):
        mock_decode.return_value = {"user_id": "123", "role": "admin"}
        with app.test_request_context(
            '/some/protected/route', headers={'Authorization': 'Bearer valid.token.here'}
        ):
            response = auth_middleware()
            self.assertIsNone(response)  # No response for valid token
            self.assertEqual(g.user_id, "123")
            self.assertEqual(g.role, "admin")

    @patch('src.app.utils.utils.Utils.decode_jwt_token')
    def test_skip_middleware_for_login_signup(self, mock_decode):
        with app.test_request_context('/login'):
            response = auth_middleware()
            self.assertIsNone(response)  # Middleware should allow these routes
        with app.test_request_context('/signup'):
            response = auth_middleware()
            self.assertIsNone(response)
