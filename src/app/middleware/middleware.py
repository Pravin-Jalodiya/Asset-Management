import jwt
from fastapi import Security, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from src.app.config.custom_error_codes import INVALID_TOKEN_ERROR, INVALID_TOKEN_PAYLOAD_ERROR, EXPIRED_TOKEN_ERROR
from src.app.models.response import CustomResponse
from src.app.utils.utils import Utils
from src.app.utils.context import set_user_to_context

security = HTTPBearer()

def auth_middleware(
    request: Request,
    credentials: HTTPAuthorizationCredentials = Security(security)
):
    # Skip auth for login and signup endpoints
    if request.url.path in ['/login', '/signup']:
        return None

    try:
        token = credentials.credentials
        # Decode the token using the secret key
        decoded_token = Utils.decode_jwt_token(token)
        print(decoded_token)
        # Extract user_id and role from the decoded token
        user_id = decoded_token.get("user_id")
        role = decoded_token.get("role")

        print(user_id, role)

        if not user_id or not role:
            return CustomResponse(
                status_code=INVALID_TOKEN_PAYLOAD_ERROR,
                message="Unauthorized, invalid token payload"
            ).object_to_dict()

        # Set user data in request context
        user_data = {
            "user_id": user_id,
            "role": role
        }

        set_user_to_context(request, user_data)

    except jwt.ExpiredSignatureError:
        return CustomResponse(
            status_code=EXPIRED_TOKEN_ERROR,
            message="Unauthorized, token has expired"
        ).object_to_dict()

    except jwt.InvalidTokenError:
        return CustomResponse(
            status_code=INVALID_TOKEN_ERROR,
            message="Unauthorized, missing or invalid token"
        ).object_to_dict()

    except Exception:
        return CustomResponse(
            status_code=INVALID_TOKEN_ERROR,
            message="Unauthorized, missing or invalid token"
        ).object_to_dict()
