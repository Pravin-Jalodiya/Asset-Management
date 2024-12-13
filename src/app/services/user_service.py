from typing import List
from AssetManagement.src.app.models.user import User, UserDTO
from AssetManagement.src.app.models.asset import Asset
from AssetManagement.src.app.models.issue import Issue
from AssetManagement.src.app.repositories.user_repository import UserRepository
from AssetManagement.src.app.utils.errors.error import (
    UserExistsError,
    InvalidCredentialsError,
    AssetNotFoundError
)
from AssetManagement.src.app.utils.utils import Utils

class UserService:
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    def signup_user(self, user: User) -> User:
        """
        Register a new user
        - Checks if user already exists
        - Hashes the password
        - Saves user to database
        """
        if self.user_repository.fetch_user_by_email(user.email) is not None:
            raise UserExistsError("User with this email already exists")

        # Hash the password
        user.password = Utils.hash_password(user.password)

        # Save to database
        self.user_repository.save_user(user)
        return user

    def login_user(self, email: str, password: str) -> User:
        """
        Authenticate user
        - Fetch user by email
        - Verify password
        """
        user = self.user_repository.fetch_user_by_email(email)
        if user is None or not Utils.check_password(password, user.password):
            raise InvalidCredentialsError("Email or password incorrect")
        return user

    def delete_user_account(self, user_id: str) -> bool:
        """
        Delete user account
        - Verify user exists before deletion
        """
        user = self.get_user_by_id(user_id)
        if user:
            return self.user_repository.delete_user(user_id)
        return False

    def get_users(self) -> List[UserDTO]:
        """
        Get all users
        """
        results = self.user_repository.fetch_users()
        return results if results else []

    def get_user_by_id(self, user_id: str) -> User | None:
        """
        Retrieve user by ID
        """
        user = self.user_repository.fetch_user_by_id(user_id)
        return user if user else None

    def get_user_by_email(self, email: str):
        """
        Retrieve user by email
        """
        user = self.user_repository.fetch_user_by_email(email)
        return user if user else None
