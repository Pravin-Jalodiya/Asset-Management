from flask import jsonify, request
from dataclasses import dataclass

from AssetManagement.src.app.models.issue import Issue
from AssetManagement.src.app.models.response import CustomResponse
from AssetManagement.src.app.services.issue_service import IssueService
from AssetManagement.src.app.utils.errors.error import NotExistsError
from AssetManagement.src.app.utils.logger.custom_logger import custom_logger
from AssetManagement.src.app.utils.logger.logger import Logger
from AssetManagement.src.app.utils.utils import Utils

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
            issues = self.issue_service.get_user_issues(user_id)
            issues = [issue.__dict__ for issue in issues] if issues else []

            if issues is not None:
                return jsonify(CustomResponse(
                    status_code=2001,  # Successfully fetched user issues
                    message="User issues fetched successfully",
                    data=issues
                ).to_dict()), 200
            else:
                return jsonify(CustomResponse(
                    status_code=4001,  # User issues not found
                    message="No issues found for the user",
                    data=None
                ).to_dict()), 404
        except Exception as e:
            self.logger.error(f"Error fetching user issues: {e}")
            return jsonify(CustomResponse(
                status_code=5001,  # Error fetching user issues
                message="Error fetching user issues",
                data=None
            ).to_dict()), 500

    @custom_logger(logger)
    @Utils.admin
    def get_issues(self):
        try:
            issues = self.issue_service.get_issues()
            issues = [issue.__dict__ for issue in issues] if issues else []

            if issues is not None:
                return jsonify(CustomResponse(
                    status_code=2002,  # Successfully fetched all issues
                    message="All issues fetched successfully",
                    data=issues
                ).to_dict()), 200
            else:
                return jsonify(CustomResponse(
                    status_code=4002,  # No issues found
                    message="No issues found",
                    data=None
                ).to_dict()), 404
        except Exception as e:
            self.logger.error(f"Error fetching all issues: {e}")
            return jsonify(CustomResponse(
                status_code=5002,  # Error fetching all issues
                message="Error fetching all issues",
                data=None
            ).to_dict()), 500

    @custom_logger(logger)
    def report_issue(self):
        """
        Report an issue
        """
        request_body = request.get_json()
        try:
            issue_data = request_body['issue']

            # Validate fields (you can add specific validation logic here)
            if not issue_data.get("asset_id") or not issue_data.get("description"):
                raise ValueError("Asset ID and description are required")

            issue_obj = Issue(
                asset_id=issue_data["asset_id"],
                description=issue_data["description"]
            )

            self.issue_service.report_issue(issue_obj)

            return jsonify(CustomResponse(
                status_code=2003,  # Successfully reported issue
                message="Issue reported successfully",
                data=None
            ).to_dict()), 200
        except ValueError as e:
            return jsonify(CustomResponse(
                status_code=4003,  # Validation error
                message=str(e),
                data=None
            ).to_dict()), 400
        except NotExistsError as e:
            return jsonify(CustomResponse(
                status_code=4104,  #  No asset found
                message=str(e),
                data=None
            ).to_dict()), 404
        except Exception as e:
            return jsonify(CustomResponse(
                status_code=5003,  # Unexpected error during issue reporting
                message="Unexpected error reporting the issue",
                data=None
            ).to_dict()), 500
