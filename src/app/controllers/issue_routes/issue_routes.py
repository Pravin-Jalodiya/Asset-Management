from flask import Blueprint

from src.app.controllers.issue_routes.issue_handlers import IssueHandler
from src.app.middleware.middleware import auth_middleware
from src.app.services.issue_service import IssueService


def create_issue_routes(issue_service: IssueService) -> Blueprint:
    issue_routes_blueprint = Blueprint('issue_routes', __name__)
    issue_routes_blueprint.before_request(auth_middleware)
    issue_handler = IssueHandler.create(issue_service)
    # Issue-related routes
    issue_routes_blueprint.add_url_rule(
        '/report-issue', 'report_issue', issue_handler.report_issue, methods=['POST']
    )

    issue_routes_blueprint.add_url_rule(
        '/issues/<user_id>', 'get_user_issues', issue_handler.get_user_issues, methods=['GET']
    )

    issue_routes_blueprint.add_url_rule(
        '/issues', 'get_issues', issue_handler.get_issues, methods=['GET']
    )

    return issue_routes_blueprint
