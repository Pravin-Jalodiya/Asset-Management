from fastapi import HTTPException, Security, Request, Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
import jwt

from src.app.config.custom_error_codes import ErrorCodes
from src.app.utils.errors.error import CustomHTTPException
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
        # Get token from credentials
        token = credentials.credentials

        # Decode the token using the secret key
        decoded_token = Utils.decode_jwt_token(token)

        # Extract user_id and role from the decoded token
        user_id = decoded_token.get("user_id")
        role = decoded_token.get("role")

        if not user_id or not role:
            raise CustomHTTPException(
                status_code=401,
                error_code=ErrorCodes.INVALID_TOKEN_PAYLOAD_ERROR,
                message="Unauthorized, invalid token payload"
            )

        # Set user data in request context
        user_data = {
            "user_id": user_id,
            "role": role
        }

        set_user_to_context(request, user_data)

    except jwt.ExpiredSignatureError:
        raise CustomHTTPException(
            status_code=401,
            error_code=ErrorCodes.EXPIRED_TOKEN_ERROR,
            message="Unauthorized, token has expired"
        )

    except jwt.InvalidTokenError:
        raise CustomHTTPException(
            status_code=401,
            error_code=ErrorCodes.INVALID_TOKEN_ERROR,
            message="Unauthorized, missing or invalid token"
        )

    except Exception as e:
        raise CustomHTTPException(
            status_code=401,
            error_code=ErrorCodes.INVALID_TOKEN_ERROR,
            message="Unauthorized, missing or invalid token"
        )
