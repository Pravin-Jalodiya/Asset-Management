import enum
from dataclasses import dataclass
from typing import Optional, Any

from starlette.responses import JSONResponse


@dataclass
class CustomResponse:
    status_code: enum
    message: str
    http_status_code: int = 200
    data: Optional[Any] = None

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
            status_code=self.http_status_code,
            content=self.object_to_dict()
        )
