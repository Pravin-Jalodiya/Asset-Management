from pydantic import BaseModel, EmailStr, UUID4, constr, validator, field_validator
from src.app.utils.validators.validators import Validators


class LoginRequest(BaseModel):
    email: EmailStr
    password: str

    @field_validator('password')
    def validate_password(cls, v):
        if not Validators.is_password_valid(v):
            raise ValueError('Password is not valid')
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "email": "user@example.com",
                "password": "StrongPass123"
            }
        }


class SignupRequest(BaseModel):
    name: str
    email: EmailStr
    password: str
    department: constr(to_upper=True)  # Automatically converts to uppercase

    @validator('name')
    def validate_name(cls, v):
        if not Validators.is_name_valid(v):
            raise ValueError('Name is not valid')
        return v

    @validator('password')
    def validate_password(cls, v):
        if not Validators.is_password_valid(v):
            raise ValueError('Password is not valid')
        return v

    @validator('department')
    def validate_department(cls, v):
        if not Validators.is_department_valid(v):
            raise ValueError('Department is not valid (dept. name should be all caps)')
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "name": "John Doe",
                "email": "john@example.com",
                "password": "StrongPass123",
                "department": "IT"
            }
        }


class ReportIssueRequest(BaseModel):
    asset_id: UUID4
    description: str

    @validator('description')
    def validate_description(cls, v):
        if not Validators.is_description_valid(v):
            raise ValueError('Description is not valid')
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

    @validator('name')
    def validate_name(cls, v):
        if not Validators.is_asset_name_valid(v):
            raise ValueError('Asset name is not valid')
        return v

    @validator('description')
    def validate_description(cls, v):
        if not Validators.is_description_valid(v):
            raise ValueError('Description is not valid')
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "name": "Laptop XPS 13",
                "description": "Dell XPS 13 laptop with 16GB RAM"
            }
        }


class AssignAssetRequest(BaseModel):
    user_id: UUID4
    asset_id: UUID4

    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "123e4567-e89b-12d3-a456-426614174000",
                "asset_id": "123e4567-e89b-12d3-a456-426614174001"
            }
        }


# UnassignAssetRequest can reuse AssignAssetRequest since they're identical
UnassignAssetRequest = AssignAssetRequest
