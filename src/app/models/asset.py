import uuid
from typing import Optional
from AssetManagement.src.app.config.types import AssetStatus

class Asset:
    def __init__(
        self,
        name: str,
        description: str,
        serial_number: Optional[str] = None,
        status: str = AssetStatus.AVAILABLE.value
    ):
        self.serial_number = serial_number if serial_number else str(uuid.uuid4())
        self.name = name
        self.description = description
        self.status = status
