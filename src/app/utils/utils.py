from bcrypt import hashpw, checkpw, gensalt
import jwt
import datetime
from functools import wraps
from fastapi import Request

from src.app.config.custom_error_codes import INVALID_TOKEN_PAYLOAD_ERROR, UNAUTHORIZED_ACCESS_ERROR, SYSTEM_ERROR
from src.app.models.response import CustomResponse
from src.app.utils.context import get_user_from_context

from src.app.config.types import Role


class Utils:
    SECRET_KEY = "SECRET"

    @staticmethod
    def hash_password(password: str) -> str:
        """
        Hash a password using bcrypt.
        """
        return hashpw(password.encode('utf-8'), gensalt()).decode('utf-8')

    @staticmethod
    def check_password(password: str, hashed_password: str) -> bool:
        """
        Verify a password against a hashed password.
        """
        return checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))

    @staticmethod
    def create_jwt_token(user_id: str, role: str) -> str:
        """
        Generates a JWT token with the provided user_id and role.

        Args:
            user_id (str): The ID of the user.
            role (str): The role of the user (e.g., "admin", "user").

        Returns:
            str: The generated JWT token.
        """
        try:
            # Define the payload
            payload = {
                "user_id": user_id,
                "role": role,
                "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=1),  # Token expires in 1 hour
                "iat": datetime.datetime.utcnow(),  # Issued at
                "nbf": datetime.datetime.utcnow(),  # Not before
            }

            # Encode the payload with the secret key
            token = jwt.encode(payload, Utils.SECRET_KEY, algorithm="HS256")

            return token
        except Exception as e:
            raise ValueError(f"Failed to generate JWT token: {str(e)}")

    @staticmethod
    def decode_jwt_token(token: str) -> dict:
        return jwt.decode(token, Utils.SECRET_KEY, algorithms=["HS256"])

    @staticmethod
    def admin(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                # Get the Request object from args or kwargs
                request = next((arg for arg in args if isinstance(arg, Request)),
                               kwargs.get('request'))

                if not request:
                    return CustomResponse(
                        status_code=INVALID_TOKEN_PAYLOAD_ERROR,
                        message="Request context not available"
                    ).object_to_dict()

                user = get_user_from_context(request)
                if not user or user.get('role') != 'admin':
                    return CustomResponse(
                        status_code=UNAUTHORIZED_ACCESS_ERROR,
                        message="Admin access required"
                    ).object_to_dict()

                return func(*args, **kwargs)

            except Exception as e:
                print(e)
                return CustomResponse(
                    status_code=SYSTEM_ERROR,
                    message="Error checking admin privileges"
                ).object_to_dict()

        return wrapper
