from flask import jsonify, request
from dataclasses import dataclass

from werkzeug.routing import ValidationError

from src.app.models.asset_issue import Issue
from src.app.models.request_objects import ReportIssueRequest
from src.app.models.response import CustomResponse
from src.app.services.asset_issue_service import IssueService
from src.app.utils.errors.error import NotExistsError, DatabaseError, NotAssignedError
from src.app.utils.logger.custom_logger import custom_logger
from src.app.utils.logger.logger import Logger
from src.app.utils.utils import Utils
from src.app.utils.validators.validators import Validators
from src.app.config.custom_error_codes import (
    INVALID_CREDENTIALS_ERROR,
    RECORD_NOT_FOUND_ERROR,
    DATABASE_OPERATION_ERROR,
    VALIDATION_ERROR,
    ASSET_NOT_FOUND_ERROR
)


@dataclass
class IssueHandler:
    issue_service: IssueService
    logger = Logger()

    @classmethod
    def create(cls, issue_service):
        return cls(issue_service)

    @custom_logger(logger)
    def get_user_issues(self, user_id: str):
        """
        Handle request for specific user issues
        """
        try:
            valid_id = Validators.is_valid_UUID(user_id)
            if valid_id:
                issues = self.issue_service.get_user_issues(user_id)
                issues = [issue.__dict__ for issue in issues] if issues else []

                if issues is not None:
                    return CustomResponse(
                        status_code=200,  # Successfully fetched user issues
                        message="User issues fetched successfully",
                        data=issues
                    ).object_to_dict(), 200

            else:
                return CustomResponse(
                    status_code=INVALID_CREDENTIALS_ERROR,
                    message="Invalid user id",
                    data=None
                ).object_to_dict(), 400

        except NotExistsError as e:
            return CustomResponse(
                status_code=RECORD_NOT_FOUND_ERROR,
                message="No such user exists",
                data=None
            ).object_to_dict(), 400

        except Exception as e:
            return CustomResponse(
                status_code=DATABASE_OPERATION_ERROR,  # Error fetching user issues
                message="Error fetching user issues",
                data=None
            ).object_to_dict(), 500

    @custom_logger(logger)
    @Utils.admin
    def get_issues(self):
        try:
            issues = self.issue_service.get_issues()
            issues = [issue.__dict__ for issue in issues] if issues else []

            if issues is not None:
                return CustomResponse(
                    status_code=200,  # Successfully fetched all issues
                    message="All issues fetched successfully",
                    data=issues
                ).object_to_dict(), 200

        except (DatabaseError, Exception) as e:
            return CustomResponse(
                status_code=DATABASE_OPERATION_ERROR,  # Error fetching all issues
                message="Error fetching all issues",
                data=None
            ).object_to_dict(), 500

    @custom_logger(logger)
    def report_issue(self):
        """
        Report an issue
        """
        try:
            issue_data = ReportIssueRequest(request.get_json())
            issue_obj = Issue(
                asset_id=issue_data.asset_id,
                description=issue_data.description
            )

            self.issue_service.report_issue(issue_obj)

            return CustomResponse(
                status_code=200,
                message="Issue reported successfully",
                data=None
            ).object_to_dict(), 200

        except ValidationError as e:
            return CustomResponse(
                status_code=VALIDATION_ERROR,  # Validation error
                message=str(e),
                data=None
            ).object_to_dict(), 400

        except NotAssignedError as e:
            return CustomResponse(
                status_code=VALIDATION_ERROR,  # Validation error
                message=str(e),
                data=None
            ).object_to_dict(), 400

        except NotExistsError as e:
            return CustomResponse(
                status_code=ASSET_NOT_FOUND_ERROR,  # No asset found
                message=str(e),
                data=None
            ).object_to_dict(), 404

        except (DatabaseError, Exception) as e:
            return CustomResponse(
                status_code=DATABASE_OPERATION_ERROR,
                message="Unexpected error reporting the issue",
                data=None
            ).object_to_dict(), 500