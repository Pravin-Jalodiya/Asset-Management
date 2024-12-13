from csv import excel

from flask import jsonify, request
from dataclasses import dataclass

from AssetManagement.src.app.models.issue import Issue
from AssetManagement.src.app.services.issue_service import IssueService
from AssetManagement.src.app.utils.logger.custom_logger import custom_logger
from AssetManagement.src.app.utils.logger.logger import Logger


@dataclass
class IssueHandler:
    issue_service: IssueService
    logger = Logger()

    @classmethod
    def create(cls, user_service):
        return cls(user_service)

    @custom_logger(logger)
    def get_user_issues(self, user_id: str):
        """
        Handle request for specific user issues
        """
        try:
            issues = self.issue_service.get_user_issues(user_id)
            issues = [issue.__dict__ for issue in issues] if issues else []
            if issues:
                return jsonify({
                    "issues": issues
                }), 200
            else:
                return jsonify({"message": "Issues not found"}), 404
        except Exception as e:
            print(e)
            return jsonify({"message": "Error fetching user issues"}), 500

    def get_issues(self):
        try:
            issues = self.issue_service.get_issues()
            issues = [issue.__dict__ for issue in issues] if issues else []

            if issues is not None:
                return jsonify({
                    "issues": issues
                }), 200
            else:
                print(issues)
                return jsonify({"message": "Issues not found"}), 404
        except Exception as e:
            return jsonify({"message": "Error fetching all issues"}), 500

    def report_issue(self):
        """
        Report an issue
        """
        request_body = request.get_json()
        try:
            issue = request_body['issue']
            print(issue)
            # validate the fields here

            issue_obj = Issue(
                asset_id=issue["asset_id"],
                description=issue["description"]
            )
            print(issue_obj)

            self.issue_service.report_issue(issue_obj)

            return jsonify({"message": "Issue reported successfully"}), 200

        except Exception as e:
            return jsonify({"message": "Error reporting the issue"}), 500
