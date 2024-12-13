from datetime import datetime, timezone

from flask import g

from AssetManagement.src.app.models.issue import Issue
from AssetManagement.src.app.repositories.issue_repository import IssueRepository

class IssueService:
    def __init__(self,issue_repository: IssueRepository):
        self.issue_repository = issue_repository

    def get_issues(self):
        """Get all issues"""
        return self.issue_repository.fetch_all_issues()

    def get_user_issues(self, user_id: str):
        """Get all user specific issues"""
        return self.issue_repository.fetch_user_issues(user_id)

    def report_issue(self, issue: Issue):
        """Report an issue"""
        issue.user_id = g.get("user_id")
        issue.report_date = datetime.now(timezone.utc)
        return self.issue_repository.report_issue(issue)
