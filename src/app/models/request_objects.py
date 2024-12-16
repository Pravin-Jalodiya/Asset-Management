from werkzeug.routing import ValidationError

from src.app.utils.errors.error import MissingFieldError
from src.app.utils.validators.validators import Validators


class LoginRequest:
    def __init__(self, data):
        try:
            self.email = data['email'].strip().lower()
            self.password = data['password'].strip()
        except KeyError as e:
            raise MissingFieldError(f"Missing field in request body: {e}")

        if not Validators.is_email_valid(self.email):
            raise ValidationError('Email is not valid')
        if not self.password:
            raise ValidationError('Password is required')


class SignupRequest:
    def __init__(self, data):
        try:
            self.name = data['name'].strip()
            self.email = data['email'].strip().lower()
            self.password = data['password'].strip()
            self.department = data['department'].strip().upper()
        except KeyError as e:
            raise MissingFieldError(f"Missing field in request body: {e}")

        if not Validators.is_name_valid(self.name):
            raise ValidationError('Name is not valid')
        if not Validators.is_email_valid(self.email):
            raise ValidationError('Email is not valid')
        if not Validators.is_password_valid(self.password):
            raise ValidationError('Password is not valid')
        if not Validators.is_department_valid(self.department):
            raise ValidationError('Department is not valid')


class ReportIssueRequest:
    def __init__(self, data):
        try:
            self.asset_id = data['asset_id'].strip().lower()
            self.description = data['description'].strip().lower()
        except KeyError as e:
            raise MissingFieldError(f"Missing field in request body: {e}")

        if not Validators.is_valid_UUID(self.asset_id):
            raise ValidationError('Asset ID is not valid')
        if self.description == "":
            raise ValidationError('Description cannot be empty')


class AssetRequest:
    def __init__(self, data):
        try:
            self.name = data['name'].strip().lower()
            self.description = data['description'].strip().lower()
        except KeyError as e:
            raise MissingFieldError(f"Missing field in request body: {e}")

        if self.name == "":
            raise ValidationError('Asset name cannot be empty')
        if self.description == "":
            raise ValidationError('Description cannot be empty')


class AssignAssetRequest:
    def __init__(self, data):
        try:
            self.user_id = data['user_id'].strip().lower()
            self.asset_id = data['asset_id'].strip().lower()
        except KeyError as e:
            raise MissingFieldError(f"Missing field in request body: {e}")

        if not Validators.is_valid_UUID(self.user_id):
            raise ValidationError('Invalid user id')
        if not Validators.is_valid_UUID(self.asset_id):
            raise ValidationError('Invalid asset id')


class UnassignAssetRequest:
    def __init__(self, data):
        try:
            self.user_id = data['user_id'].strip().lower()
            self.asset_id = data['asset_id'].strip().lower()
        except KeyError as e:
            raise MissingFieldError(f"Missing field in request body: {e}")

        if not Validators.is_valid_UUID(self.user_id):
            raise ValidationError('Invalid user id')
        if not Validators.is_valid_UUID(self.asset_id):
            raise ValidationError('Invalid asset id')
