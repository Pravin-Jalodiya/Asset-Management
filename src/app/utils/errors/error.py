class UserError(Exception):
    """Base exception class for all user-related errors"""
    pass


class UserExistsError(UserError):
    """Raised when attempting to create a user that already exists"""

    def __init__(self, message: str):
        super().__init__(message)


class InvalidCredentialsError(UserError):
    """ Raised when invalid credentials are entered (email or password) """

    def __init__(self, message: str):
        super().__init__(f"{message}")


class DatabaseError(Exception):
    """Base exception class for all database-related errors"""

    def __init__(self, message: str):
        super().__init__(message)


class NotExistsError(Exception):
    """Base exception class for no entries found"""

    def __init__(self, message: str):
        super().__init__(message)


class ExistsError(Exception):
    """Base exception class for entries already present"""

    def __init__(self, message: str):
        super().__init__(message)


class InvalidOperationError(Exception):
    """Base exception class for invalid operations"""

    def __init__(self, message: str):
        super().__init__(message)


class AssetNotFoundError(Exception):
    """Base exception class for asset not found"""

    def __init__(self, message: str):
        super().__init__(message)

class AssetAlreadyAssignedError(Exception):
    """Base exception class for asset already assigned"""

    def __init__(self, message: str):
        super().__init__(message)

class NotAssignedError(Exception):
    """Base exception class for asset not assigned"""

    def __init__(self, message: str):
        super().__init__(message)

class AlreadyAssignedError(Exception):
    """Base exception class for asset already assigned"""

    def __init__(self, message: str):
        super().__init__(message)