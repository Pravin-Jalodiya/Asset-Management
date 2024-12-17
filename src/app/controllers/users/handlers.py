from flask import request
from werkzeug.routing import ValidationError
from dataclasses import dataclass

from src.app.models.request_objects import LoginRequest, SignupRequest
from src.app.models.response import CustomResponse
from src.app.models.user import User
from src.app.services.user_service import UserService
from src.app.utils.logger.custom_logger import custom_logger
from src.app.utils.utils import Utils
from src.app.utils.logger.logger import Logger
from src.app.utils.errors.error import (
    UserExistsError,
    InvalidCredentialsError, MissingFieldError, DatabaseError,
)
from src.app.utils.validators.validators import Validators

# Importing the new error codes
from src.app.config.custom_error_codes import (
    VALIDATION_ERROR,
    MISSING_FIELD_ERROR,
    INVALID_CREDENTIALS_ERROR,
    USER_EXISTS_ERROR,
    DATABASE_OPERATION_ERROR,
    RECORD_NOT_FOUND_ERROR,
    USER_NOT_FOUND_ERROR
)

@dataclass
class UserHandler:
    user_service: UserService
    logger = Logger()

    @classmethod
    def create(cls, user_service):
        return cls(user_service)

    @custom_logger(logger)
    def login(self):
        try:
            login_data = LoginRequest(request.get_json())
            user = self.user_service.login_user(login_data.email, login_data.password)
            token = Utils.create_jwt_token(user.id, user.role)

            return CustomResponse(
                status_code=200,
                message="Login successful",
                data={
                    'token': token,
                    'role': user.role,
                    'user_id': user.id
                }
            ).object_to_dict(), 200

        except ValidationError as e:
            return CustomResponse(
                status_code=VALIDATION_ERROR,
                message=str(e),
                data=None
            ).object_to_dict(), 400

        except MissingFieldError as e:
            return CustomResponse(
                status_code=MISSING_FIELD_ERROR,
                message=str(e),
                data=None
            ).object_to_dict(), 400

        except InvalidCredentialsError as e:
            return CustomResponse(
                status_code=INVALID_CREDENTIALS_ERROR,
                message="Invalid email or password",
                data=None
            ).object_to_dict(), 400

        except (DatabaseError, Exception) as e:
            return CustomResponse(
                status_code=DATABASE_OPERATION_ERROR,
                message="Unexpected error during login",
                data=None
            ).object_to_dict(), 500

    def signup(self):
        try:
            signup_data = SignupRequest(request.get_json())

            user = User(
                name=signup_data.name,
                email=signup_data.email,
                password=signup_data.password,
                department=signup_data.department
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
            ).object_to_dict(), 200

        except ValidationError as e:
            return CustomResponse(
                status_code=VALIDATION_ERROR,
                message=str(e),
                data=None
            ).object_to_dict(), 400

        except MissingFieldError as e:
            return CustomResponse(
                status_code=MISSING_FIELD_ERROR,
                message=str(e),
                data=None
            ).object_to_dict(), 400

        except UserExistsError as e:
            return CustomResponse(
                status_code=USER_EXISTS_ERROR,
                message=str(e),
                data=None
            ).object_to_dict(), 409

        except (DatabaseError, Exception) as e:
            return CustomResponse(
                status_code=DATABASE_OPERATION_ERROR,
                message="Unexpected error during signup",
                data=None
            ).object_to_dict(), 500

    @custom_logger(logger)
    @Utils.admin
    def get_users(self):
        try:
            results = self.user_service.get_users()
            results = [result.__dict__ for result in results] if results else []

            if results is not None:
                return CustomResponse(
                    status_code=200,
                    message="Users fetched successfully",
                    data=results
                ).object_to_dict(), 200

        except (DatabaseError, Exception) as e:
            return CustomResponse(
                status_code=DATABASE_OPERATION_ERROR,
                message="Error fetching users",
                data=None
            ).object_to_dict(), 500

    @custom_logger(logger)
    def get_user(self, user_id: str):
        try:
            result = self.user_service.get_user_by_id(user_id).__dict__

            if result is not None:
                return CustomResponse(
                    status_code=200,
                    message="User details retrieved successfully",
                    data=result
                ).object_to_dict(), 200
            else:
                return CustomResponse(
                    status_code=USER_NOT_FOUND_ERROR,
                    message="User not found",
                    data=None
                ).object_to_dict(), 404

        except (DatabaseError, Exception) as e:
            return CustomResponse(
                status_code=DATABASE_OPERATION_ERROR,
                message="Error fetching user details",
                data=None
            ).object_to_dict(), 500

    @custom_logger(logger)
    @Utils.admin
    def delete_user(self, user_id: str):
        try:
            valid_id = Validators.is_valid_UUID(user_id)
            if valid_id:
                success = self.user_service.delete_user_account(user_id)

                if success:
                    return CustomResponse(
                        status_code=200,
                        message="User account deleted successfully",
                        data=None
                    ).object_to_dict(), 200
                else:
                    return CustomResponse(
                        status_code=USER_NOT_FOUND_ERROR,
                        message="User not found",
                        data=None
                    ).object_to_dict(), 404

            else:
                return CustomResponse(
                    status_code=200,
                    message="Invalid user id",
                    data=None
                ).object_to_dict(), 200

        except ValueError as e:
            return CustomResponse(
                status_code=RECORD_NOT_FOUND_ERROR,
                message="Invalid user id",
                data=None
            ).object_to_dict(), 400

        except (DatabaseError, Exception) as e:
            return CustomResponse(
                status_code=DATABASE_OPERATION_ERROR,
                message="Error deleting account",
                data=None
            ).object_to_dict(), 500