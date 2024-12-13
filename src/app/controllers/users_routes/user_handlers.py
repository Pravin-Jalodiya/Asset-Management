from flask import Blueprint, request, jsonify, g
from werkzeug.routing import ValidationError
from dataclasses import dataclass

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
            return jsonify({
                'token': token,
                'role': user.role,
                'user_id': user.id
            }), 200
        except (ValidationError, InvalidCredentialsError) as e:
            return jsonify({"message": str(e)}), 400
        except Exception as e:
            return jsonify({"message": f"Unexpected error during login {str(e)}"}), 500

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

            return jsonify({
                'token': token,
                'role': user.role,
                'user_id': user.id
            }), 200
        except UserExistsError as e:
            return jsonify({"message": str(e)}), 409
        except (ValidationError, ValueError) as e:
            return jsonify({"message": str(e)}), 400
        except Exception as e:
            return jsonify({"message": f"Unexpected error during signup: {str(e)}"}), 500


    @custom_logger(logger)
    def get_users(self):
        """
        Handle request for all users' details
        """
        try:
            results = self.user_service.get_users()
            results = [result.__dict__ for result in results] if results else []
            if results is not None:
                return jsonify({
                    "users": results
                }), 200
            else:
                return jsonify({"message": "Users not found"}), 404
        except Exception as e:
            print(e)
            return jsonify({"message": f"Error fetching users"}), 500

    @custom_logger(logger)
    def get_user(self, user_id: str):
        """
        Handle request for specific user details
        """
        try:
            result = self.user_service.get_user_by_id(user_id).__dict__

            if result:
                return jsonify({
                    "user": result
                }), 200
            else:
                return jsonify({"message": "User not found"}), 404
        except Exception as e:
            return jsonify({"message": "Error fetching user"}), 500

    @custom_logger(logger)
    def delete_user(self, user_id: str):
        """
        Handle user account deletion
        - Verify user authentication
        - Delete account
        """
        try:
            success = self.user_service.delete_user_account(user_id)
            if success:
                return jsonify({"message": "User account deleted successfully"}), 200
            else:
                return jsonify({"message": "User not found"}), 404
        except Exception as e:
            return jsonify({"message": "Error deleting account"}), 500