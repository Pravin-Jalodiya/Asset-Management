from dataclasses import dataclass

from src.app.config.custom_error_codes import ErrorCodes
from src.app.models.request_objects import SignupRequest, LoginRequest
from src.app.models.response import CustomResponse
from src.app.models.user import User
from src.app.services.user_service import UserService
from src.app.utils.errors.error import UserExistsError, InvalidCredentialsError
from src.app.utils.logger.custom_logger import custom_logger
from src.app.utils.logger.logger import Logger
from src.app.utils.utils import Utils


@dataclass
class AuthHandler:
    user_service: UserService
    logger = Logger()

    @classmethod
    def create(cls, user_service: UserService):
        return cls(user_service)

    @custom_logger(logger)
    def signup(self, user_data: SignupRequest):
        try:
            user = User(
                name=user_data.name,
                email=user_data.email,
                password=user_data.password,
                department=user_data.department
            )

            self.user_service.signup_user(user)
            token = Utils.create_jwt_token(user.id, user.role)

            return CustomResponse(
                status_code=200,
                message="User registered successfully",
                data={
                    'token': token,
                    'role': user.role,
                    'user_id': user.id
                }
            ).object_to_dict()

        except UserExistsError as e:
            return CustomResponse(
                status_code=ErrorCodes.USER_EXISTS_ERROR,
                message=str(e)
            ).object_to_dict()

        except Exception as e:
            return CustomResponse(
                status_code=ErrorCodes.DATABASE_OPERATION_ERROR,
                message="Error creating user",
                http_status_code=500
            ).to_response()

    @custom_logger(logger)
    def login(self, credentials: LoginRequest):
        try:
            self.logger.info(credentials)
            user = self.user_service.login_user(str(credentials.email), credentials.password)
            token = Utils.create_jwt_token(user.id, user.role)

            return CustomResponse(
                status_code=200,
                message="Login successful",
                data={
                    'token': token,
                    'role': user.role,
                    'user_id': user.id
                }
            ).object_to_dict()

        except InvalidCredentialsError as e:
            return CustomResponse(
                status_code=ErrorCodes.INVALID_CREDENTIALS_ERROR,
                message=str(e)
            ).object_to_dict()

        except Exception as e:
            return CustomResponse(
                status_code=ErrorCodes.DATABASE_OPERATION_ERROR,
                message="Unexpected error during login",
                http_status_code=500
            ).to_response()
