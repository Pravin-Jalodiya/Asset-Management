import unittest
from unittest.mock import patch, MagicMock
import jwt
from fastapi import Request
from fastapi.security import HTTPAuthorizationCredentials
from src.app.middleware.middleware import auth_middleware
from src.app.config.custom_error_codes import ErrorCodes

class TestAuthMiddleware(unittest.TestCase):

    def setUp(self):
        # Create base mock request
        self.mock_scope = {
            "type": "http",
            "headers": [],
            "method": "GET",
            "path": "/",
            "query_string": b"",
            "client": ("127.0.0.1", 8000),
        }

    @patch('src.app.utils.utils.Utils.decode_jwt_token')
    async def test_expired_token(self, mock_decode):
        mock_decode.side_effect = jwt.ExpiredSignatureError
        request = Request(self.mock_scope)
        credentials = HTTPAuthorizationCredentials(
            scheme="Bearer",
            credentials="expired.token.here"
        )

        try:
            await auth_middleware(request, credentials)
            self.fail("Should have raised an exception")
        except Exception as e:
            self.assertEqual(e.status_code, 401)
            self.assertEqual(e.error_code, ErrorCodes.EXPIRED_TOKEN_ERROR)
            self.assertEqual(str(e), "Unauthorized, token has expired")

    @patch('src.app.utils.utils.Utils.decode_jwt_token')
    async def test_invalid_token(self, mock_decode):
        mock_decode.side_effect = jwt.InvalidTokenError
        request = Request(self.mock_scope)
        credentials = HTTPAuthorizationCredentials(
            scheme="Bearer",
            credentials="invalid.token.here"
        )

        try:
            await auth_middleware(request, credentials)
            self.fail("Should have raised an exception")
        except Exception as e:
            self.assertEqual(e.status_code, 401)
            self.assertEqual(e.error_code, ErrorCodes.INVALID_TOKEN_ERROR)
            self.assertEqual(str(e), "Unauthorized, missing or invalid token")

    @patch('src.app.utils.utils.Utils.decode_jwt_token')
    async def test_invalid_token_payload(self, mock_decode):
        mock_decode.return_value = {"invalid_key": "value"}
        request = Request(self.mock_scope)
        credentials = HTTPAuthorizationCredentials(
            scheme="Bearer",
            credentials="valid.token.here"
        )

        try:
            await auth_middleware(request, credentials)
            self.fail("Should have raised an exception")
        except Exception as e:
            self.assertEqual(e.status_code, 401)
            self.assertEqual(e.error_code, ErrorCodes.INVALID_TOKEN_PAYLOAD_ERROR)
            self.assertEqual(str(e), "Unauthorized, invalid token payload")

    @patch('src.app.utils.utils.Utils.decode_jwt_token')
    async def test_valid_token(self, mock_decode):
        mock_decode.return_value = {"user_id": "123", "role": "admin"}
        request = Request(self.mock_scope)
        credentials = HTTPAuthorizationCredentials(
            scheme="Bearer",
            credentials="valid.token.here"
        )

        result = await auth_middleware(request, credentials)
        self.assertIsNone(result)
        # Check if user data was set in request state
        self.assertEqual(request.state.user["user_id"], "123")
        self.assertEqual(request.state.user["role"], "admin")

    async def test_skip_middleware_for_login_signup(self):
        # Test login endpoint
        login_scope = self.mock_scope.copy()
        login_scope["path"] = "/login"
        login_request = Request(login_scope)
        
        result = await auth_middleware(login_request, None)
        self.assertIsNone(result)

        # Test signup endpoint
        signup_scope = self.mock_scope.copy()
        signup_scope["path"] = "/signup"
        signup_request = Request(signup_scope)
        
        result = await auth_middleware(signup_request, None)
        self.assertIsNone(result)
