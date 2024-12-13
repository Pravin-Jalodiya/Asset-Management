import uuid
from dataclasses import dataclass
from typing import Optional
from datetime import datetime, timezone

@dataclass
class Issue:

    def __init__(
        self,
        asset_id: str,
        description: str,
        user_id: Optional[str] = None,
        issue_id: Optional[str] = None,
        report_date: Optional[datetime] = None,
    ):
        self.issue_id = issue_id if issue_id else str(uuid.uuid4())
        self.user_id = user_id
        self.asset_id = asset_id
        self.description = description
        self.report_date = report_date if report_date else datetime.now(timezone.utc)