from bcrypt import hashpw, checkpw, gensalt
import jwt
import datetime

from flask import jsonify,g

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
    def admin(f):
        def wrapped_func(*args, **kwargs):
            # Check if the user role in g is 'admin'
            if g.get("role") != Role.ADMIN.value:
                return jsonify({"message": "Unauthorized: Admin role required"}), 403
            return f(*args, **kwargs)

        return wrapped_func
