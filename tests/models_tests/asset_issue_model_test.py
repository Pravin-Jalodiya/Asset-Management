import unittest
from datetime import datetime, timezone
from uuid import UUID

from src.app.models.asset_issue import Issue


class TestIssue(unittest.TestCase):
    def setUp(self):
        """Set up tests fixtures before each tests method."""
        self.asset_id = "ASSET001"
        self.description = "Test Description"
        self.user_id = "USER001"
        self.issue_id = "ISSUE001"
        self.report_date = datetime.now(timezone.utc)

    def test_issue_creation_with_all_parameters(self):
        """Test issue creation with all parameters provided."""
        # Arrange & Act
        issue = Issue(
            asset_id=self.asset_id,
            description=self.description,
            user_id=self.user_id,
            issue_id=self.issue_id,
            report_date=self.report_date
        )

        # Assert
        self.assertEqual(issue.asset_id, self.asset_id)
        self.assertEqual(issue.description, self.description)
        self.assertEqual(issue.user_id, self.user_id)
        self.assertEqual(issue.issue_id, self.issue_id)
        self.assertEqual(issue.report_date, self.report_date)

    def test_issue_creation_with_minimum_parameters(self):
        """Test issue creation with only required parameters."""
        # Arrange & Act
        issue = Issue(
            asset_id=self.asset_id,
            description=self.description
        )

        # Assert
        self.assertEqual(issue.asset_id, self.asset_id)
        self.assertEqual(issue.description, self.description)
        self.assertIsNone(issue.user_id)
        self.assertIsInstance(UUID(issue.issue_id), UUID)  # Verify UUID format
        self.assertIsInstance(issue.report_date, datetime)
        self.assertEqual(issue.report_date.tzinfo, timezone.utc)  # Verify UTC timezone

    def test_issue_creation_without_optional_parameters(self):
        """Test issue creation without optional parameters generates default values."""
        # Arrange & Act
        before_creation = datetime.now(timezone.utc)
        issue = Issue(
            asset_id=self.asset_id,
            description=self.description
        )
        after_creation = datetime.now(timezone.utc)

        # Assert
        self.assertIsNotNone(issue.issue_id)
        self.assertIsInstance(UUID(issue.issue_id), UUID)
        self.assertIsNone(issue.user_id)
        self.assertGreaterEqual(issue.report_date, before_creation)
        self.assertLessEqual(issue.report_date, after_creation)

    def test_issue_creation_with_custom_issue_id(self):
        """Test issue creation with custom issue_id."""
        # Arrange
        custom_issue_id = "CUSTOM_ID_001"

        # Act
        issue = Issue(
            asset_id=self.asset_id,
            description=self.description,
            issue_id=custom_issue_id
        )

        # Assert
        self.assertEqual(issue.issue_id, custom_issue_id)

    def test_issue_creation_with_user_id_only(self):
        """Test issue creation with user_id but default issue_id and report_date."""
        # Act
        issue = Issue(
            asset_id=self.asset_id,
            description=self.description,
            user_id=self.user_id
        )

        # Assert
        self.assertEqual(issue.user_id, self.user_id)
        self.assertIsInstance(UUID(issue.issue_id), UUID)
        self.assertIsInstance(issue.report_date, datetime)

    def test_issue_creation_with_custom_report_date(self):
        """Test issue creation with custom report_date."""
        # Arrange
        custom_date = datetime(2024, 1, 1, tzinfo=timezone.utc)

        # Act
        issue = Issue(
            asset_id=self.asset_id,
            description=self.description,
            report_date=custom_date
        )

        # Assert
        self.assertEqual(issue.report_date, custom_date)

    def test_required_parameters(self):
        """Test that asset_id and description are required."""
        # Assert
        with self.assertRaises(TypeError):
            Issue(asset_id=self.asset_id)  # Missing description

        with self.assertRaises(TypeError):
            Issue(description=self.description)  # Missing asset_id
