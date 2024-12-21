import uuid
from typing import Optional
from src.app.config.types import Role, AssetStatus


class   User:
    def __init__(
            self,
            name: str,
            email: str,
            password: str,
            department: str,
            id: str = None,
            role: str = Role.USER.value
    ):
        self.id = id if id else str(uuid.uuid4())
        self.name = name
        self.email = email
        self.department = department
        self.password = password
        self.role = role


class UserDTO:
    def __init__(
            self,
            id: str,
            name: str,
            email: str,
            department: str,
    ):
        self.id = id
        self.name = name
        self.email = email
        self.department = department
