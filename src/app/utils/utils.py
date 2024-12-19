from bcrypt import hashpw, checkpw, gensalt
import jwt
import datetime
from functools import wraps
from fastapi import Request
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
        async def wrapper(*args, **kwargs):
            try:
                # Get the Request object from kwargs
                request = next((arg for arg in args if isinstance(arg, Request)), 
                             kwargs.get('request'))
                
                if not request:
                    return CustomResponse(
                        status_code=500,
                        message="Request context not available"
                    )

                user = get_user_from_context(request)
                if not user or user.get('role') != 'ADMIN':
                    return CustomResponse(
                        status_code=403,
                        message="Admin access required"
                    )
                
                return await func(*args, **kwargs)
                
            except Exception as e:
                return CustomResponse(
                    status_code=500,
                    message="Error checking admin privileges"
                )
                
        return wrapper
