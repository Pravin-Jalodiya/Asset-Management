import uuid

import pytest
from unittest.mock import Mock
from flask import Flask, g

from src.app.config.custom_error_codes import INVALID_CREDENTIALS_ERROR, RECORD_NOT_FOUND_ERROR, \
    DATABASE_OPERATION_ERROR, VALIDATION_ERROR, ASSET_NOT_FOUND_ERROR
from src.app.models.asset_issue import Issue
from src.app.utils.errors.error import NotExistsError, DatabaseError, NotAssignedError
from src.app.controllers.asset_issue.handlers import IssueHandler


@pytest.fixture
def app():
    """Flask application fixture"""
    app = Flask(__name__)
    return app


@pytest.fixture
def mock_issue_service():
    """Mock issue service fixture"""
    return Mock()


@pytest.fixture
def issue_handler(mock_issue_service):
    """Issue handler fixture with mocked service"""
    return IssueHandler.create(mock_issue_service)


@pytest.fixture
def sample_issue():
    """Sample issue fixture"""
    return Issue(
        asset_id="550e8400-e29b-41d4-a716-446655440000",
        description="Test issue"
    )


@pytest.fixture
def sample_issues():
    """Sample list of issues fixture"""
    return [
        Issue(
            asset_id="550e8400-e29b-41d4-a716-446655440000",
            description="First issue"
        ),
        Issue(
            asset_id="650e8400-e29b-41d4-a716-446655440000",
            description="Second issue"
        )
    ]


class TestIssueHandler:
    def test_get_user_issues_success(self, app, issue_handler, sample_issues):
        """Test successful retrieval of user issues"""
        valid_user_id = "550e8400-e29b-41d4-a716-446655440000"
        issue_handler.issue_service.get_user_issues.return_value = sample_issues

        with app.test_request_context():
            response, status_code = issue_handler.get_user_issues(valid_user_id)

        assert status_code == 200
        assert response["status_code"] == 200
        assert response["message"] == "User issues fetched successfully"
        assert len(response["data"]) == 2
        assert response["data"][0]["description"] == "First issue"

        issue_handler.issue_service.get_user_issues.assert_called_once_with(valid_user_id)

    def test_get_user_issues_invalid_uuid(self, app, issue_handler):
        """Test get user issues with invalid UUID"""
        invalid_user_id = "invalid-uuid"

        with app.test_request_context():
            response, status_code = issue_handler.get_user_issues(invalid_user_id)

        assert status_code == 400
        assert response["status_code"] == INVALID_CREDENTIALS_ERROR  # INVALID_CREDENTIALS_ERROR
        assert response["message"] == "Invalid user id"

    def test_get_user_issues_user_not_found(self, app, issue_handler):
        """Test get user issues when user doesn't exist"""
        valid_user_id = str(uuid.uuid4())
        issue_handler.issue_service.get_user_issues.side_effect = NotExistsError("No such user exists")

        with app.test_request_context():
            response, status_code = issue_handler.get_user_issues(valid_user_id)

        assert status_code == 400
        assert response["status_code"] == RECORD_NOT_FOUND_ERROR
        assert response["message"] == "No such user exists"

    def test_get_user_issues_database_error(self, app, issue_handler):
        """Test get user issues with database error"""
        valid_user_id = "550e8400-e29b-41d4-a716-446655440000"
        issue_handler.issue_service.get_user_issues.side_effect = Exception("Database error")

        with app.test_request_context():
            response, status_code = issue_handler.get_user_issues(valid_user_id)

        assert status_code == 500
        assert response["status_code"] == DATABASE_OPERATION_ERROR
        assert response["message"] == "Error fetching user issues"


    def test_get_issues_success(self, app, issue_handler, sample_issues):
        """Test successful retrieval of all issues"""
        issue_handler.issue_service.get_issues.return_value = sample_issues

        with app.test_request_context():
            g.role = 'admin'
            response, status_code = issue_handler.get_issues()

        assert status_code == 200
        assert response["status_code"] == 200
        assert response["message"] == "All issues fetched successfully"
        assert len(response["data"]) == 2

        issue_handler.issue_service.get_issues.assert_called_once()

    def test_get_issues_database_error(self, app, issue_handler):
        """Test get all issues with database error"""
        issue_handler.issue_service.get_issues.side_effect = DatabaseError("Database error")

        with app.test_request_context():
            g.role = 'admin'
            response, status_code = issue_handler.get_issues()

        assert status_code == 500
        assert response["status_code"] == DATABASE_OPERATION_ERROR
        assert response["message"] == "Error fetching all issues"

    def test_report_issue_success(self, app, issue_handler, sample_issue):
        """Test successful issue reporting"""
        request_data = {
            "asset_id": "550e8400-e29b-41d4-a716-446655440000",
            "description": "Test issue"
        }

        with app.test_request_context(json=request_data):
            response, status_code = issue_handler.report_issue()

        assert status_code == 200
        assert response["status_code"] == 200
        assert response["message"] == "Issue reported successfully"

        issue_handler.issue_service.report_issue.assert_called_once()

    def test_report_issue_validation_error(self, app, issue_handler):
        """Test report issue with validation error"""
        request_data = {
            "asset_id": "invalid-uuid",
            "description": "Test issue"
        }

        with app.test_request_context(json=request_data):
            response, status_code = issue_handler.report_issue()

        assert status_code == 400
        assert response["status_code"] == VALIDATION_ERROR

    def test_report_issue_not_assigned_error(self, app, issue_handler):
        """Test report issue with not assigned error"""
        request_data = {
            "asset_id": "550e8400-e29b-41d4-a716-446655440000",
            "description": "Test issue"
        }
        issue_handler.issue_service.report_issue.side_effect = NotAssignedError("Asset not assigned")

        with app.test_request_context(json=request_data):
            response, status_code = issue_handler.report_issue()

        assert status_code == 400
        assert response["status_code"] == VALIDATION_ERROR

    def test_report_issue_asset_not_found(self, app, issue_handler):
        """Test report issue with non-existent asset"""
        request_data = {
            "asset_id": "550e8400-e29b-41d4-a716-446655440000",
            "description": "Test issue"
        }
        issue_handler.issue_service.report_issue.side_effect = NotExistsError("Asset not found")

        with app.test_request_context(json=request_data):
            response, status_code = issue_handler.report_issue()

        assert status_code == 404
        assert response["status_code"] == ASSET_NOT_FOUND_ERROR

    def test_report_issue_database_error(self, app, issue_handler):
        """Test report issue with database error"""
        request_data = {
            "asset_id": "550e8400-e29b-41d4-a716-446655440000",
            "description": "Test issue"
        }
        issue_handler.issue_service.report_issue.side_effect = DatabaseError("Database error")

        with app.test_request_context(json=request_data):
            response, status_code = issue_handler.report_issue()

        assert status_code == 500
        assert response["status_code"] == DATABASE_OPERATION_ERROR
        assert response["message"] == "Unexpected error reporting the issue"