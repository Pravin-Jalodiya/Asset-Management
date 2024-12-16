from datetime import datetime, timezone

from flask import g

from src.app.models.issue import Issue
from src.app.repositories.issue_repository import IssueRepository
from src.app.services.asset_service import AssetService
from src.app.services.user_service import UserService
from src.app.utils.errors.error import NotExistsError, NotAssignedError


class IssueService:
    def __init__(self,issue_repository: IssueRepository, asset_service: AssetService, user_service: UserService):
        self.issue_repository = issue_repository
        self.asset_service = asset_service
        self.user_service = user_service

    def get_issues(self):
        """Get all issues"""
        return self.issue_repository.fetch_all_issues()

    def get_user_issues(self, user_id: str):
        """Get all user specific issues"""
        if self.user_service.get_user_by_id(user_id) is None:
            raise NotExistsError("No such user exists")
        return self.issue_repository.fetch_user_issues(user_id)

    def report_issue(self, issue: Issue):
        """Report an issue"""
        if self.asset_service.get_asset_by_id(issue.asset_id) is None:
            raise NotExistsError("No such asset exists")

        issue.user_id = g.get("user_id")
        if not self.asset_service.is_asset_assigned(issue.user_id, issue.asset_id):
            raise NotAssignedError("Asset not assigned to user")

        issue.report_date = datetime.now(timezone.utc)
        return self.issue_repository.report_issue(issue)
