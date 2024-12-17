import jwt
from flask import request, jsonify, g

from src.app.config.custom_error_codes import INVALID_TOKEN_ERROR, INVALID_TOKEN_PAYLOAD_ERROR, EXPIRED_TOKEN_ERROR
from src.app.models.response import CustomResponse
from src.app.utils.utils import Utils

def auth_middleware():
    if request.path in ['/login', '/signup']:
        return None

    auth_token = request.headers.get('Authorization')
    if not auth_token or not auth_token.startswith('Bearer '):
        return CustomResponse(
            status_code=INVALID_TOKEN_ERROR,
            message="Unauthorized, missing or invalid token",
            data=None
        ).object_to_dict(), 401

    token = auth_token.split(' ')[1]
    try:
        # Decode the token using the secret key
        decoded_token = Utils.decode_jwt_token(token)

        # Extract user_id and role from the decoded token
        user_id = decoded_token.get("user_id")
        role = decoded_token.get("role")

        if not user_id or not role:
            return CustomResponse(
                status_code=INVALID_TOKEN_PAYLOAD_ERROR,
                message="Unauthorized, invalid token payload",
                data=None
            ).object_to_dict(), 401

        # Set user_id and role in Flask's global context
        g.user_id = user_id
        g.role = role

    except jwt.ExpiredSignatureError:
        return CustomResponse(
            status_code=EXPIRED_TOKEN_ERROR,
            message="Unauthorized, token has expired",
            data=None
        ).object_to_dict(), 401
    except jwt.InvalidTokenError:
        return CustomResponse(
            status_code=INVALID_TOKEN_ERROR,
            message="Unauthorized, missing or invalid token",
            data=None
        ).object_to_dict(), 401
