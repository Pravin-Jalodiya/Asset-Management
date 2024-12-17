import pytest
from unittest.mock import MagicMock
from flask import Flask, g, request
from src.app.controllers.asset_issue.handlers import IssueHandler
from src.app.utils.errors.error import NotExistsError, DatabaseError, NotAssignedError
from src.app.models.asset_issue import Issue


class TestIssueHandler:
    @pytest.fixture
    def app(self):
        """Create a Flask app instance for testing"""
        app = Flask(__name__)
        app.config["TESTING"] = True
        return app

    @pytest.fixture
    def mock_issue_service(self):
        """Create a mock IssueService for testing"""
        return MagicMock()

    @pytest.fixture
    def issue_handler(self, mock_issue_service):
        """Create an IssueHandler instance with mock issue service"""
        return IssueHandler.create(mock_issue_service)

    def test_get_user_issues_success(self, issue_handler, mock_issue_service, app):
        """Test successful retrieval of user issues"""
        # Prepare mock data
        user_id = "550e8400-e29b-41d4-a716-446655440000"
        mock_issues = [
            MagicMock(id="issue1"),
            MagicMock(id="issue2")
        ]
        mock_issue_service.get_user_issues.return_value = mock_issues

        # Mock the validator
        with pytest.MonkeyPatch.context() as m:
            m.setattr('src.app.controller.issue_urls.issue_routes.Validators.is_valid_UUID', return_value=True)

            with app.test_request_context():
                response, status_code = issue_handler.get_user_issues(user_id)

                assert status_code == 200
                assert response['message'] == "User issues fetched successfully"
                assert len(response['data']) == 2
                mock_issue_service.get_user_issues.assert_called_once_with(user_id)

    def test_get_user_issues_invalid_uuid(self, issue_handler, mock_issue_service, app):
        """Test get user issues with invalid UUID"""
        # Mock the validator to return False
        with pytest.MonkeyPatch.context() as m:
            m.setattr('src.app.controller.issue_urls.issue_routes.Validators.is_valid_UUID', return_value=False)

            with app.test_request_context():
                response, status_code = issue_handler.get_user_issues("invalid-uuid")

                assert status_code == 400
                assert response['message'] == "Invalid user id"
                mock_issue_service.get_user_issues.assert_not_called()

    def test_get_user_issues_not_exists(self, issue_handler, mock_issue_service, app):
        """Test get user issues for non-existent user"""
        # Prepare mock data
        user_id = "550e8400-e29b-41d4-a716-446655440000"
        mock_issue_service.get_user_issues.side_effect = NotExistsError("No such user")

        # Mock the validator
        with pytest.MonkeyPatch.context() as m:
            m.setattr('src.app.controller.issue_urls.issue_routes.Validators.is_valid_UUID', return_value=True)

            with app.test_request_context():
                response, status_code = issue_handler.get_user_issues(user_id)

                assert status_code == 400
                assert response['message'] == "No such user exists"

    def test_get_issues_admin_success(self, issue_handler, mock_issue_service, app):
        """Test successful retrieval of all issues by admin"""
        # Prepare mock data
        mock_issues = [
            MagicMock(id="issue1"),
            MagicMock(id="issue2")
        ]
        mock_issue_service.get_issues.return_value = mock_issues

        # Create a mock for the admin decorator
        def mock_admin_decorator(func):
            def wrapper(*args, **kwargs):
                return func(*args, **kwargs)

            return wrapper

        with pytest.MonkeyPatch.context() as m:
            m.setattr('src.app.controller.issue_urls.issue_routes.Utils.admin', mock_admin_decorator)

            with app.test_request_context():
                response, status_code = issue_handler.get_issues()

                assert status_code == 200
                assert response['message'] == "All issues fetched successfully"
                assert len(response['data']) == 2
                mock_issue_service.get_issues.assert_called_once()

    def test_get_issues_database_error(self, issue_handler, mock_issue_service, app):
        """Test get issues with database error"""
        mock_issue_service.get_issues.side_effect = DatabaseError("Database error")

        # Create a mock for the admin decorator
        def mock_admin_decorator(func):
            def wrapper(*args, **kwargs):
                return func(*args, **kwargs)

            return wrapper

        with pytest.MonkeyPatch.context() as m:
            m.setattr('src.app.controller.issue_urls.issue_routes.Utils.admin', mock_admin_decorator)

            with app.test_request_context():
                response, status_code = issue_handler.get_issues()

                assert status_code == 500
                assert response['message'] == "Error fetching all issues"

    def test_report_issue_success(self, issue_handler, mock_issue_service, app):
        """Test successful issue reporting"""
        # Prepare test data
        issue_data = {
            "asset_id": "asset123",
            "description": "Test issue description"
        }

        with app.test_request_context(json=issue_data):
            response, status_code = issue_handler.report_issue()

            assert status_code == 200
            assert response['message'] == "Issue reported successfully"
            mock_issue_service.report_issue.assert_called_once()

    def test_report_issue_not_assigned(self, issue_handler, mock_issue_service, app):
        """Test reporting issue when asset is not assigned"""
        # Prepare test data
        issue_data = {
            "asset_id": "asset123",
            "description": "Test issue description"
        }

        mock_issue_service.report_issue.side_effect = NotAssignedError("Asset not assigned")

        with app.test_request_context(json=issue_data):
            response, status_code = issue_handler.report_issue()

            assert status_code == 400
            assert str(response['message']) == "Asset not assigned"

    def test_report_issue_asset_not_found(self, issue_handler, mock_issue_service, app):
        """Test reporting issue for non-existent asset"""
        # Prepare test data
        issue_data = {
            "asset_id": "asset123",
            "description": "Test issue description"
        }

        mock_issue_service.report_issue.side_effect = NotExistsError("Asset not found")

        with app.test_request_context(json=issue_data):
            response, status_code = issue_handler.report_issue()

            assert status_code == 404
            assert str(response['message']) == "Asset not found"

    def test_report_issue_database_error(self, issue_handler, mock_issue_service, app):
        """Test reporting issue with unexpected database error"""
        # Prepare test data
        issue_data = {
            "asset_id": "asset123",
            "description": "Test issue description"
        }

        mock_issue_service.report_issue.side_effect = DatabaseError("Unexpected database error")

        with app.test_request_context(json=issue_data):
            response, status_code = issue_handler.report_issue()

            assert status_code == 4002
            assert response['message'] == "Unexpected error reporting the issue"