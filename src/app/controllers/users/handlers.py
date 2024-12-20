from dataclasses import dataclass
from fastapi import Request

from src.app.models.user import User
from src.app.models.request_objects import SignupRequest, LoginRequest
from src.app.services.user_service import UserService
from src.app.utils.errors.error import NotExistsError, InvalidCredentialsError, UserExistsError
from src.app.utils.logger.custom_logger import custom_logger
from src.app.utils.logger.logger import Logger
from src.app.utils.utils import Utils
from src.app.models.response import CustomResponse
from src.app.config.custom_error_codes import (
    INVALID_CREDENTIALS_ERROR,
    USER_EXISTS_ERROR,
    USER_NOT_FOUND_ERROR,
    DATABASE_OPERATION_ERROR,
)

@dataclass
class UserHandler:
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
                email=str(user_data.email),
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
                status_code=USER_EXISTS_ERROR,
                message=str(e)
            ).object_to_dict()

        except Exception as e:
            return CustomResponse(
                status_code=DATABASE_OPERATION_ERROR,
                message="Error creating user"
            ).object_to_dict()

    @custom_logger(logger)
    def login(self, credentials: LoginRequest):
        try:
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
                status_code=INVALID_CREDENTIALS_ERROR,
                message=str(e)
            ).object_to_dict()

        except Exception as e:
            return CustomResponse(
                status_code=DATABASE_OPERATION_ERROR,
                message="Unexpected error during login"
            ).object_to_dict()

    @custom_logger(logger)
    def get_user(self, user_id: str):
        try:
            user = self.user_service.get_user_by_id(user_id)
            return CustomResponse(
                status_code=200,
                message="User fetched successfully",
                data=user.__dict__
            ).object_to_dict()

        except NotExistsError as e:
            return CustomResponse(
                status_code=USER_NOT_FOUND_ERROR,
                message=str(e)
            ).object_to_dict()

        except Exception as e:
            return CustomResponse(
                status_code=DATABASE_OPERATION_ERROR,
                message="Error fetching user"
            ).object_to_dict()

    @custom_logger(logger)
    @Utils.admin
    def get_users(self, request: Request):
        try:
            users = self.user_service.get_users()
            return CustomResponse(
                status_code=200,
                message="Users fetched successfully",
                data=[user.__dict__ for user in users] if users else []
            ).object_to_dict()

        except Exception as e:
            return CustomResponse(
                status_code=DATABASE_OPERATION_ERROR,
                message="Error fetching users"
            ).object_to_dict()

    @custom_logger(logger)
    @Utils.admin
    def delete_user(self, request: Request, user_id: str):
        try:
            self.user_service.delete_user_account(user_id)
            return CustomResponse(
                status_code=200,
                message="User deleted successfully"
            ).object_to_dict()

        except NotExistsError as e:
            return CustomResponse(
                status_code=USER_NOT_FOUND_ERROR,
                message=str(e)
            ).object_to_dict()

        except Exception as e:
            return CustomResponse(
                status_code=DATABASE_OPERATION_ERROR,
                message="Error deleting user"
            ).object_to_dict()
