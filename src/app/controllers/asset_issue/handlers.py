from dataclasses import dataclass
from src.app.models.asset_issue import Issue
from src.app.models.request_objects import ReportIssueRequest
from src.app.services.asset_issue_service import IssueService
from src.app.utils.errors.error import NotExistsError, NotAssignedError
from src.app.utils.logger.custom_logger import custom_logger
from src.app.utils.logger.logger import Logger
from src.app.utils.utils import Utils
from src.app.models.response import CustomResponse

@dataclass
class IssueHandler:
    issue_service: IssueService
    logger = Logger()

    @classmethod
    def create(cls, issue_service):
        return cls(issue_service)

    @custom_logger(logger)
    async def get_user_issues(self, user_id: str):
        try:
            issues = await self.issue_service.get_user_issues(user_id)
            return CustomResponse(
                status_code=200,
                message="User issues fetched successfully",
                data=[issue.dict() for issue in issues] if issues else []
            )
        except NotExistsError as e:
            return CustomResponse(
                status_code=404,
                message=str(e)
            )
        except Exception as e:
            return CustomResponse(
                status_code=500,
                message="Error fetching user issues"
            )

    @custom_logger(logger)
    @Utils.admin
    async def get_issues(self):
        try:
            issues = await self.issue_service.get_issues()
            return CustomResponse(
                status_code=200,
                message="All issues fetched successfully",
                data=[issue.dict() for issue in issues] if issues else []
            )
        except Exception as e:
            return CustomResponse(
                status_code=500,
                message="Error fetching all issues"
            )

    @custom_logger(logger)
    async def report_issue(self, issue_data: ReportIssueRequest):
        try:
            issue_obj = Issue(
                asset_id=str(issue_data.asset_id),
                description=issue_data.description
            )
            await self.issue_service.report_issue(issue_obj)
            return CustomResponse(
                status_code=201,
                message="Issue reported successfully",
                data=issue_obj.dict()
            )
        except NotAssignedError as e:
            return CustomResponse(
                status_code=400,
                message=str(e)
            )
        except NotExistsError as e:
            return CustomResponse(
                status_code=404,
                message=str(e)
            )
        except Exception as e:
            return CustomResponse(
                status_code=500,
                message="Unexpected error reporting the issue"
            )