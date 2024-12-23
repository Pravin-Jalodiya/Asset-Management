from dataclasses import dataclass
from fastapi import Request

from src.app.services.user_service import UserService
from src.app.utils.errors.error import NotExistsError
from src.app.utils.logger.custom_logger import custom_logger
from src.app.utils.logger.logger import Logger
from src.app.utils.utils import Utils
from src.app.models.response import CustomResponse
from src.app.config.custom_error_codes import ErrorCodes


@dataclass
class UserHandler:
    user_service: UserService
    logger = Logger()

    @classmethod
    def create(cls, user_service: UserService):
        return cls(user_service)

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
                status_code=ErrorCodes.USER_NOT_FOUND_ERROR,
                message=str(e)
            ).object_to_dict()

        except Exception as e:
            return CustomResponse(
                status_code=ErrorCodes.DATABASE_OPERATION_ERROR,
                message="Error fetching user",
                http_status_code=500
            ).to_response()

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
                status_code=ErrorCodes.DATABASE_OPERATION_ERROR,
                message="Error fetching users",
                http_status_code=500
            ).to_response()

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
                status_code=ErrorCodes.USER_NOT_FOUND_ERROR,
                message=str(e)
            ).object_to_dict()

        except Exception as e:
            return CustomResponse(
                status_code=ErrorCodes.DATABASE_OPERATION_ERROR,
                message="Error deleting user",
                http_status_code=500
            ).to_response()
