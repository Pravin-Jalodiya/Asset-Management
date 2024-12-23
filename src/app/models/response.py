import enum
from dataclasses import dataclass
from typing import Optional, Any

from starlette.responses import JSONResponse
from src.app.config.custom_error_codes import ErrorCodes


@dataclass
class CustomResponse:
    status_code: enum
    message: str
    http_status_code: int = 200
    data: Optional[Any] = None

    def __init__(self, status_code, message, data=None, http_status_code=None):
        self.status_code = status_code.value if isinstance(status_code, ErrorCodes) else status_code
        self.message = message
        self.data = data
        self.http_status_code = http_status_code

    def object_to_dict(self):
        response = {
            'status_code': self.status_code,
            'message': self.message,
        }

        if self.data is not None:
            response.update({'data': self.data})

        return response

    def to_response(self):
        """Convert to FastAPI JSONResponse with proper HTTP status code"""
        return JSONResponse(
            status_code=self.http_status_code or 200,
            content=self.object_to_dict()
        )
