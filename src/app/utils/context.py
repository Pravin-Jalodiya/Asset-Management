from fastapi import Request
from typing import Optional

def get_user_from_context(request: Request) -> Optional[dict]:
    """Get user data from request state"""
    return getattr(request.state, "user", None)

def set_user_to_context(request: Request, user_data: dict):
    """Set user data to request state"""
    request.state.user = user_data 