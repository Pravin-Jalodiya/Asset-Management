from fastapi import HTTPException
from pydantic import BaseModel, field_validator

from src.app.config.custom_error_codes import ErrorCodes
from src.app.utils.errors.error import CustomHTTPException
from src.app.utils.validators.validators import Validators


class LoginRequest(BaseModel):
    email: str
    password: str

    @field_validator('email')
    def validate_email(v: str):
        if not Validators.is_email_valid(v):
            raise CustomHTTPException(
                status_code=400,
                error_code=ErrorCodes.VALIDATION_ERROR,
                message='Invalid email (supported domain(s) : [@watchguard.com])'
            )
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "email": "user@watchguard.com",
                "password": "Strongpass@123"
            }
        }


class SignupRequest(BaseModel):
    name: str
    email: str
    password: str
    department: str

    @field_validator('name')
    def validate_name(v: str):
        if not Validators.is_name_valid(v):
            raise CustomHTTPException(
                status_code=400,
                error_code=ErrorCodes.VALIDATION_ERROR,
                message='Invalid name'
            )
        return v

    @field_validator('password')
    def validate_password(v: str) -> str:
        if not Validators.is_password_valid(v):
            raise CustomHTTPException(
                status_code=400,
                error_code=ErrorCodes.VALIDATION_ERROR,
                message='Invalid password'
            )
        return v

    @field_validator('email')
    def validate_email(v: str) -> str:
        if not Validators.is_email_valid(str(v)):
            raise CustomHTTPException(
                status_code=400,
                error_code=ErrorCodes.VALIDATION_ERROR,
                message='Invalid email (supported domain(s) : [@watchguard.com])'
            )
        return v

    @field_validator('department')
    def validate_department(v: str) -> str:
        if not Validators.is_department_valid(v):
            raise CustomHTTPException(
                status_code=400,
                error_code=ErrorCodes.VALIDATION_ERROR,
                message='Invalid department (dept. name should be all caps)'
            )
        return v

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

    @field_validator('asset_id')
    def validate_uuid(v: str):
        if not Validators.is_valid_UUID(v):
            raise CustomHTTPException(
                status_code=400,
                error_code=ErrorCodes.VALIDATION_ERROR,
                message=f'{v} is not a valid UUID'
            )
        return v

    @field_validator('description')
    def validate_description(v: str):
        if not v:
            raise CustomHTTPException(
                status_code=400,
                error_code=ErrorCodes.VALIDATION_ERROR,
                message='Description cannot be empty'
            )
        return v

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

    @field_validator('name')
    def validate_name(v: str):
        if not v:
            raise CustomHTTPException(
                status_code=400,
                error_code=ErrorCodes.VALIDATION_ERROR,
                message='Asset name cannot be empty'
            )
        return v

    @field_validator('description')
    def validate_description(v: str):
        if not v:
            raise CustomHTTPException(
                status_code=400,
                error_code=ErrorCodes.VALIDATION_ERROR,
                message='Description cannot be empty'
            )
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "name": "Laptop XPS 13",
                "description": "Dell XPS 13 laptop with 16GB RAM and Intel i13 processor"
            }
        }


class AssignAssetRequest(BaseModel):
    user_id: str
    asset_id: str

    @field_validator('user_id', 'asset_id')
    def validate_uuid(v: str):
        if not Validators.is_valid_UUID(v):
            raise CustomHTTPException(
                status_code=400,
                error_code=ErrorCodes.VALIDATION_ERROR,
                message=f"{v} is not a valid UUID"
            )
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "123e4567-e89b-12d3-a456-426614174000",
                "asset_id": "123e4567-e89b-12d3-a456-426614174001"
            }
        }


UnassignAssetRequest = AssignAssetRequest
