from dataclasses import dataclass
from fastapi import Request

from src.app.models.asset_issue import Issue
from src.app.models.request_objects import ReportIssueRequest
from src.app.services.asset_issue_service import IssueService
from src.app.utils.errors.error import NotExistsError, NotAssignedError
from src.app.utils.logger.custom_logger import custom_logger
from src.app.utils.logger.logger import Logger
from src.app.utils.utils import Utils
from src.app.models.response import CustomResponse
from src.app.config.custom_error_codes import ErrorCodes

@dataclass
class IssueHandler:
    issue_service: IssueService
    logger = Logger()

    @classmethod
    def create(cls, issue_service):
        return cls(issue_service)

    @custom_logger(logger)
    def get_user_issues(self, user_id: str):
        try:
            issues = self.issue_service.get_user_issues(user_id)
            return CustomResponse(
                status_code=200,
                message="User issues fetched successfully",
                data=[issue.__dict__ for issue in issues] if issues else []
            ).object_to_dict()

        except NotExistsError as e:
            return CustomResponse(
                status_code=ErrorCodes.RECORD_NOT_FOUND_ERROR,
                message=str(e)
            ).object_to_dict()

        except Exception as e:
            return CustomResponse(
                status_code=ErrorCodes.DATABASE_OPERATION_ERROR,
                message="Error fetching user issues",
                http_status_code=500
            ).to_response()

    @custom_logger(logger)
    @Utils.admin
    def get_issues(self, request: Request):
        try:
            issues = self.issue_service.get_issues()
            return CustomResponse(
                status_code=200,
                message="All issues fetched successfully",
                data=[issue.__dict__ for issue in issues] if issues else []
            ).object_to_dict()

        except Exception as e:
            return CustomResponse(
                status_code=ErrorCodes.DATABASE_OPERATION_ERROR,
                message="Error fetching all issues",
                http_status_code=500
            ).to_response()

    @custom_logger(logger)
    def report_issue(self, request: Request, issue_data: ReportIssueRequest):
        try:
            issue_obj = Issue(
                asset_id=str(issue_data.asset_id),
                description=issue_data.description
            )

            self.issue_service.report_issue(request, issue_obj)
            return CustomResponse(
                status_code=200,
                message="Issue reported successfully",
                data=issue_obj.__dict__
            ).object_to_dict()

        except NotAssignedError as e:
            return CustomResponse(
                status_code=ErrorCodes.ASSET_NOT_ASSIGNED_ERROR,
                message=str(e)
            ).object_to_dict()

        except NotExistsError as e:
            return CustomResponse(
                status_code=ErrorCodes.ASSET_NOT_FOUND_ERROR,
                message=str(e)
            ).object_to_dict()

        except Exception as e:
            return CustomResponse(
                status_code=ErrorCodes.DATABASE_OPERATION_ERROR,
                message="Unexpected error reporting the issue",
                http_status_code=500
            ).to_response()
