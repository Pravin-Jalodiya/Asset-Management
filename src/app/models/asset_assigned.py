import uuid
from datetime import datetime, timezone


class AssetAssigned:
    def __init__(
        self,
        user_id: str,
        asset_id: str,
        asset_assigned_id:str = None,
        assigned_date: datetime = None
    ):
        self.asset_assigned_id = asset_assigned_id if asset_assigned_id else str(uuid.uuid4())
        self.user_id = user_id
        self.asset_id = asset_id
        self.assigned_date = assigned_date if assigned_date else datetime.now(timezone.utc)
