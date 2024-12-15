from flask import Blueprint, request, jsonify, g
from werkzeug.routing import ValidationError
from dataclasses import dataclass

from AssetManagement.src.app.models.response import CustomResponse
from AssetManagement.src.app.models.user import User
from AssetManagement.src.app.services.user_service import UserService
from AssetManagement.src.app.utils.logger.custom_logger import custom_logger
from AssetManagement.src.app.utils.utils import Utils
from AssetManagement.src.app.utils.validators.validators import Validators
from AssetManagement.src.app.utils.logger.logger import Logger
from AssetManagement.src.app.utils.errors.error import (
    UserExistsError,
    InvalidCredentialsError,
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
        """
        Handle user login
        - Validate email and password
        - Generate JWT token
        """
        request_body = request.get_json()
        try:
            email = request_body['email'].strip().lower()
            if not Validators.is_email_valid(email):
                raise ValidationError('Email is not valid')

            password = request_body['password'].strip()
            user = self.user_service.login_user(email, password)

            token = Utils.create_jwt_token(user.id, user.role)
            return jsonify(CustomResponse(
                status_code=2001,  # Successful login
                message="Login successful",
                data={
                    'token': token,
                    'role': user.role,
                    'user_id': user.id
                }
            ).to_dict()), 200
        except ValidationError as e:
            return jsonify(CustomResponse(
                status_code=4001,  # Email validation error
                message=str(e),
                data=None
            ).to_dict()), 400
        except InvalidCredentialsError as e:
            return jsonify(CustomResponse(
                status_code=4002,  # Invalid login credentials
                message="Invalid email or password",
                data=None
            ).to_dict()), 400
        except Exception as e:
            return jsonify(CustomResponse(
                status_code=5001,  # Unexpected login error
                message="Unexpected error during login",
                data=None
            ).to_dict()), 500

    @custom_logger(logger)
    def signup(self):
        """
        Handle user signup
        - Validate all input fields
        - Create user
        - Generate JWT token
        """
        request_body = request.get_json()
        try:
            # Validate and extract input fields
            name = request_body['name'].strip()
            if not Validators.is_name_valid(name):
                raise ValidationError('Name is not valid')

            email = request_body['email'].strip().lower()
            if not Validators.is_email_valid(email):
                raise ValidationError('Email is not valid')

            password = request_body['password'].strip()
            if not Validators.is_password_valid(password):
                raise ValidationError('Password is not valid')

            department = request_body['department'].strip()
            if not Validators.is_department_valid(department):
                raise ValidationError('Department is not valid')

            # Create user
            user = User(
                name=name,
                email=email,
                password=password,
                department=department
            )

            # Signup and generate token
            self.user_service.signup_user(user)
            token = Utils.create_jwt_token(user.id, user.role)

            return jsonify(CustomResponse(
                status_code=2002,  # Successful signup
                message="User registered successfully",
                data={
                    'token': token,
                    'role': user.role,
                    'user_id': user.id
                }
            ).to_dict()), 200
        except UserExistsError as e:
            return jsonify(CustomResponse(
                status_code=4003,  # User already exists
                message=str(e),
                data=None
            ).to_dict()), 409
        except (ValidationError, ValueError) as e:
            return jsonify(CustomResponse(
                status_code=4004,  # Validation error during signup
                message=str(e),
                data=None
            ).to_dict()), 400
        except Exception as e:
            return jsonify(CustomResponse(
                status_code=5002,  # Unexpected signup error
                message=f"Unexpected error during signup",
                data=None
            ).to_dict()), 500

    @custom_logger(logger)
    @Utils.admin
    def get_users(self):
        """
        Handle request for all users' details
        """
        try:
            results = self.user_service.get_users()
            results = [result.__dict__ for result in results] if results else []
            if results is not None:
                return jsonify(CustomResponse(
                    status_code=2003,  # Successfully fetched users
                    message="Users fetched successfully",
                    data=results
                ).to_dict()), 200
            else:
                return jsonify(CustomResponse(
                    status_code=4005,  # No users found
                    message="No users found",
                    data=None
                ).to_dict()), 404
        except Exception as e:
            return jsonify(CustomResponse(
                status_code=5003,  # Error fetching users
                message="Error fetching users",
                data=None
            ).to_dict()), 500

    @custom_logger(logger)
    def get_user(self, user_id: str):
        """
        Handle request for specific user details
        """
        try:
            result = self.user_service.get_user_by_id(user_id).__dict__

            if result is not None:
                return jsonify(CustomResponse(
                    status_code=2004,  # Successfully fetched user
                    message="User details retrieved successfully",
                    data=result
                ).to_dict()), 200
            else:
                return jsonify(CustomResponse(
                    status_code=4006,  # User not found
                    message="User not found",
                    data=None
                ).to_dict()), 404
        except Exception as e:
            return jsonify(CustomResponse(
                status_code=5004,  # Error fetching user details
                message="Error fetching user details",
                data=None
            ).to_dict()), 500

    @custom_logger(logger)
    @Utils.admin
    def delete_user(self, user_id: str):
        """
        Handle user account deletion
        - Verify user authentication
        - Delete account
        """
        try:
            success = self.user_service.delete_user_account(user_id)
            if success:
                return jsonify(CustomResponse(
                    status_code=2005,  # Successfully deleted user
                    message="User account deleted successfully",
                    data=None
                ).to_dict()), 200
            else:
                return jsonify(CustomResponse(
                    status_code=4007,  # User not found for deletion
                    message="User not found",
                    data=None
                ).to_dict()), 404
        except Exception as e:
            return jsonify(CustomResponse(
                status_code=5005,  # Error deleting account
                message="Error deleting account",
                data=None
            ).to_dict()), 500