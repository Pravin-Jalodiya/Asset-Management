from datetime import datetime, timezone

from flask import g

from AssetManagement.src.app.models.issue import Issue
from AssetManagement.src.app.repositories.issue_repository import IssueRepository
from AssetManagement.src.app.services.asset_service import AssetService
from AssetManagement.src.app.utils.errors.error import NotExistsError


class IssueService:
    def __init__(self,issue_repository: IssueRepository, asset_service: AssetService):
        self.issue_repository = issue_repository
        self.asset_service = asset_service

    def get_issues(self):
        """Get all issues"""
        return self.issue_repository.fetch_all_issues()

    def get_user_issues(self, user_id: str):
        """Get all user specific issues"""
        return self.issue_repository.fetch_user_issues(user_id)

    def report_issue(self, issue: Issue):
        """Report an issue"""
        if self.asset_service.get_asset_by_id(issue.asset_id) is None:
            raise NotExistsError("Asset does not exist")
        issue.user_id = g.get("user_id")
        issue.report_date = datetime.now(timezone.utc)
        return self.issue_repository.report_issue(issue)
