import unittest
from unittest.mock import MagicMock
from datetime import datetime, timezone
from flask import Flask, g
from src.app.models.asset_issue import Issue
from src.app.services.asset_issue_service import IssueService
from src.app.utils.errors.error import NotExistsError, NotAssignedError


class TestIssueService(unittest.TestCase):
    def setUp(self):
        # Create Flask app and context
        self.app = Flask(__name__)
        self.app_context = self.app.app_context()
        self.app_context.push()

        # Create mock dependencies
        self.mock_issue_repository = MagicMock()
        self.mock_asset_service = MagicMock()
        self.mock_user_service = MagicMock()

        # Initialize service with mock dependencies
        self.issue_service = IssueService(
            self.mock_issue_repository,
            self.mock_asset_service,
            self.mock_user_service
        )

    def tearDown(self):
        # Remove the application context
        self.app_context.pop()

    def test_get_issues_returns_all_issues(self):
        # Arrange
        expected_issues = [
            Issue(
                asset_id="asset1",
                description="Issue with asset 1",
                user_id="user1",
                issue_id="issue1",
                report_date=datetime.now(timezone.utc)
            ),
            Issue(
                asset_id="asset2",
                description="Issue with asset 2",
                user_id="user2",
                issue_id="issue2",
                report_date=datetime.now(timezone.utc)
            )
        ]
        self.mock_issue_repository.fetch_all_issues.return_value = expected_issues

        # Act
        result = self.issue_service.get_issues()

        # Assert
        self.mock_issue_repository.fetch_all_issues.assert_called_once()
        self.assertEqual(result, expected_issues)

    def test_get_user_issues_returns_user_specific_issues(self):
        # Arrange
        user_id = "user1"
        expected_issues = [
            Issue(
                asset_id="asset1",
                description="First issue",
                user_id=user_id,
                issue_id="issue1",
                report_date=datetime.now(timezone.utc)
            ),
            Issue(
                asset_id="asset2",
                description="Second issue",
                user_id=user_id,
                issue_id="issue2",
                report_date=datetime.now(timezone.utc)
            )
        ]
        self.mock_user_service.get_user_by_id.return_value = {"id": user_id}
        self.mock_issue_repository.fetch_user_issues.return_value = expected_issues

        # Act
        result = self.issue_service.get_user_issues(user_id)

        # Assert
        self.mock_user_service.get_user_by_id.assert_called_once_with(user_id)
        self.mock_issue_repository.fetch_user_issues.assert_called_once_with(user_id)
        self.assertEqual(result, expected_issues)

    def test_get_user_issues_raises_error_for_nonexistent_user(self):
        # Arrange
        user_id = "nonexistent_user"
        self.mock_user_service.get_user_by_id.return_value = None

        # Act & Assert
        with self.assertRaises(NotExistsError) as context:
            self.issue_service.get_user_issues(user_id)

        self.assertEqual(str(context.exception), "No such user exists")
        self.mock_user_service.get_user_by_id.assert_called_once_with(user_id)
        self.mock_issue_repository.fetch_user_issues.assert_not_called()

    def test_report_issue_successful(self):
        # Arrange
        user_id = "user1"
        asset_id = "asset1"
        with self.app.test_request_context():
            g.user_id = user_id  # Set user_id in Flask g context

            issue = Issue(
                asset_id=asset_id,
                description="Test issue description",
                user_id=None,
            )

            self.mock_asset_service.get_asset_by_id.return_value = {"id": asset_id}
            self.mock_asset_service.is_asset_assigned.return_value = True
            self.mock_issue_repository.report_issue.return_value = issue

            # Act
            result = self.issue_service.report_issue(issue)

            # Assert
            self.mock_asset_service.get_asset_by_id.assert_called_once_with(asset_id)
            self.mock_asset_service.is_asset_assigned.assert_called_once_with(user_id, asset_id)
            self.mock_issue_repository.report_issue.assert_called_once_with(issue)
            self.assertEqual(result, issue)
            self.assertEqual(result.user_id, user_id)
            self.assertIsNotNone(result.report_date)
            self.assertIsNotNone(result.issue_id)

    def test_report_issue_raises_error_for_nonexistent_asset(self):
        # Arrange
        user_id = "user1"
        asset_id = "nonexistent_asset"
        with self.app.test_request_context():
            g.user_id = user_id

            issue = Issue(
                asset_id=asset_id,
                description="Test issue description",
                user_id=None,
            )

            self.mock_asset_service.get_asset_by_id.return_value = None

            # Act & Assert
            with self.assertRaises(NotExistsError) as context:
                self.issue_service.report_issue(issue)

            self.assertEqual(str(context.exception), "No such asset exists")
            self.mock_asset_service.get_asset_by_id.assert_called_once_with(asset_id)
            self.mock_asset_service.is_asset_assigned.assert_not_called()
            self.mock_issue_repository.report_issue.assert_not_called()

    def test_report_issue_raises_error_for_unassigned_asset(self):
        # Arrange
        user_id = "user1"
        asset_id = "asset1"
        with self.app.test_request_context():
            g.user_id = user_id

            issue = Issue(
                asset_id=asset_id,
                description="Test issue description",
                user_id=None,
            )

            self.mock_asset_service.get_asset_by_id.return_value = {"id": asset_id}
            self.mock_asset_service.is_asset_assigned.return_value = False

            # Act & Assert
            with self.assertRaises(NotAssignedError) as context:
                self.issue_service.report_issue(issue)

            self.assertEqual(str(context.exception), "Asset not assigned to user")
            self.mock_asset_service.get_asset_by_id.assert_called_once_with(asset_id)
            self.mock_asset_service.is_asset_assigned.assert_called_once_with(user_id, asset_id)
            self.mock_issue_repository.report_issue.assert_not_called()
