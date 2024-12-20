from pydantic import BaseModel, EmailStr, field_validator
from werkzeug.routing import ValidationError

from src.app.utils.validators.validators import Validators


class LoginRequest(BaseModel):
    email: EmailStr
    password: str

    @classmethod
    @field_validator('email')
    def validate_email(cls, v):
        if not Validators.is_email_valid(v):
            raise ValidationError('Invalid email (supported domain(s) : [@watchguard.com])')

    @classmethod
    @field_validator('password')
    def validate_password(cls, v):
        if not Validators.is_password_valid(v):
            raise ValidationError('Invalid password')

    class Config:
        json_schema_extra = {
            "example": {
                "email": "user@watchguard.com",
                "password": "Strongpass@123"
            }
        }


class SignupRequest(BaseModel):
    name: str
    email: EmailStr
    password: str
    department: str

    @classmethod
    @field_validator('name')
    def validate_name(cls, v):
        if not Validators.is_name_valid(v):
            raise ValidationError('Invalid name')

    @classmethod
    @field_validator('password')
    def validate_password(cls, v):
        if not Validators.is_password_valid(v):
            raise ValidationError('Invalid password')

    @classmethod
    @field_validator('email')
    def validate_email(cls, v):
        if not Validators.is_email_valid(str(v)):
            raise ValidationError('Invalid email (supported domain(s) : [@watchguard.com])')

    @classmethod
    @field_validator('department')
    def validate_department(cls, v):
        if not Validators.is_department_valid(v):
            raise ValidationError('Invalid department (dept. name should be all caps)')

    class Config:
        json_schema_extra = {
            "example": {
                "name": "John Doe",
                "email": "john@watchguard.com",
                "password": "Strongpass@123",
                "department": "CLOUD PLATFORM"
            }
        }


class ReportIssueRequest(BaseModel):
    asset_id: str
    description: str

    @classmethod
    @field_validator('asset_id')
    def validate_uuid(cls, v):
        if not Validators.is_valid_UUID(v):
            raise ValidationError(f'{v} is not a valid UUID')

    @classmethod
    @field_validator('description')
    def validate_description(cls, v):
        if not v:
            raise ValidationError('Description cannot be empty')

    class Config:
        json_schema_extra = {
            "example": {
                "asset_id": "123e4567-e89b-12d3-a456-426614174000",
                "description": "Screen not working"
            }
        }


class AssetRequest(BaseModel):
    name: str
    description: str

    @classmethod
    @field_validator('name')
    def validate_name(cls, v):
        if not v:
            raise ValidationError('Asset name cannot be empty')

    @classmethod
    @field_validator('description')
    def validate_description(cls, v):
        if not v:
            raise ValidationError('Description cannot be empty')

    class Config:
        json_schema_extra = {
            "example": {
                "name": "Laptop XPS 13",
                "description": "Dell XPS 13 laptop with 16GB RAM and intel i13 processor"
            }
        }


class AssignAssetRequest(BaseModel):
    user_id: str
    asset_id: str

    @classmethod
    @field_validator('user_id', 'asset_id')
    def validate_uuid(cls, v: str):
        if not Validators.is_valid_UUID(v):
            raise ValidationError(f"{v} is not a valid UUID")

    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "123e4567-e89b-12d3-a456-426614174000",
                "asset_id": "123e4567-e89b-12d3-a456-426614174001"
            }
        }


UnassignAssetRequest = AssignAssetRequest
