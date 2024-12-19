from dataclasses import dataclass
from src.app.models.user import User
from src.app.models.request_objects import SignupRequest, LoginRequest
from src.app.services.user_service import UserService
from src.app.utils.errors.error import ValidationError, NotExistsError, AlreadyExistsError, AuthenticationError
from src.app.utils.logger.custom_logger import custom_logger
from src.app.utils.logger.logger import Logger
from src.app.utils.utils import Utils
from src.app.models.response import CustomResponse

@dataclass
class UserHandler:
    user_service: UserService
    logger = Logger()

    @classmethod
    def create(cls, user_service: UserService):
        return cls(user_service)

    @custom_logger(logger)
    async def signup(self, user_data: SignupRequest):
        try:
            user = User(
                name=user_data.name,
                email=user_data.email,
                password=user_data.password,
                department=user_data.department
            )
            await self.user_service.add_user(user)
            return CustomResponse(
                status_code=201,
                message="User created successfully",
                data=user.dict(exclude={'password'})
            )
        except (ValidationError, AlreadyExistsError) as e:
            return CustomResponse(
                status_code=400,
                message=str(e)
            )
        except Exception as e:
            return CustomResponse(
                status_code=500,
                message="Error creating user"
            )

    @custom_logger(logger)
    async def login(self, credentials: LoginRequest):
        try:
            token = await self.user_service.authenticate_user(
                credentials.email,
                credentials.password
            )
            return CustomResponse(
                status_code=200,
                message="Login successful",
                data={"token": token}
            )
        except AuthenticationError as e:
            return CustomResponse(
                status_code=401,
                message=str(e)
            )
        except Exception as e:
            return CustomResponse(
                status_code=500,
                message="Login error"
            )

    @custom_logger(logger)
    async def get_user(self, user_id: str):
        try:
            user = await self.user_service.get_user(user_id)
            return CustomResponse(
                status_code=200,
                message="User fetched successfully",
                data=user.dict(exclude={'password'})
            )
        except NotExistsError as e:
            return CustomResponse(
                status_code=404,
                message=str(e)
            )
        except Exception as e:
            return CustomResponse(
                status_code=500,
                message="Error fetching user"
            )

    @custom_logger(logger)
    @Utils.admin
    async def get_users(self, department: str = None):
        try:
            users = await self.user_service.get_users(department)
            return CustomResponse(
                status_code=200,
                message="Users fetched successfully",
                data=[user.dict(exclude={'password'}) for user in users] if users else []
            )
        except Exception as e:
            return CustomResponse(
                status_code=500,
                message="Error fetching users"
            )

    @custom_logger(logger)
    @Utils.admin
    async def delete_user(self, user_id: str):
        try:
            await self.user_service.delete_user(user_id)
            return CustomResponse(
                status_code=200,
                message="User deleted successfully"
            )
        except NotExistsError as e:
            return CustomResponse(
                status_code=404,
                message=str(e)
            )
        except Exception as e:
            return CustomResponse(
                status_code=500,
                message="Error deleting user"
            )