import unittest
from unittest.mock import MagicMock, patch
from datetime import datetime
from src.app.repositories.asset_issue_repository import IssueRepository
from src.app.models.asset_issue import Issue
from src.app.utils.errors.error import DatabaseError


class TestIssueRepository(unittest.TestCase):
    @patch("src.app.utils.db.db.DB")
    def setUp(self, mock_db):
        # Initialize mocked DB and QueryBuilder
        self.mock_db = mock_db

        # Mock DB connection and cursor
        self.mock_conn = MagicMock()
        self.mock_cursor = MagicMock()
        self.mock_db.get_connection.return_value = self.mock_conn
        self.mock_conn.cursor.return_value = self.mock_cursor

        # Initialize IssueRepository with mocked DB
        self.issue_repository = IssueRepository(self.mock_db)

    @patch("src.app.utils.db.query_builder.GenericQueryBuilder.insert")
    def test_report_issue_success(self, mock_query_builder):
        # Arrange
        current_time = datetime.now()
        issue = Issue(
            issue_id="ISS001",
            user_id="U001",
            asset_id="SN001",
            description="Screen not working",
            report_date=current_time
        )

        issue_data = {
            "issue_id": issue.issue_id,
            "user_id": issue.user_id,
            "asset_id": issue.asset_id,
            "description": issue.description,
            "report_date": issue.report_date
        }

        query = "INSERT INTO issues ..."
        values = tuple(issue_data.values())
        mock_query_builder.return_value = (query, values)

        # Act
        self.issue_repository.report_issue(issue)

        # Assert
        mock_query_builder.assert_called_once_with("issues", issue_data)
        self.mock_cursor.execute.assert_called_once_with(query, values)

    def test_report_issue_raises_database_error(self):
        # Arrange
        issue = Issue(
            issue_id="ISS001",
            user_id="U001",
            asset_id="SN001",
            description="Screen not working",
            report_date=datetime.now()
        )
        self.mock_conn.cursor.side_effect = Exception("Database connection error")

        # Act & Assert
        with self.assertRaises(DatabaseError):
            self.issue_repository.report_issue(issue)

    @patch("src.app.utils.db.query_builder.GenericQueryBuilder.select")
    def test_fetch_all_issues_success(self, mock_query_builder):
        # Arrange
        current_time = datetime.now()
        mock_results = [
            ("ISS001", "U001", "SN001", "Screen not working", current_time),
            ("ISS002", "U002", "SN002", "Keyboard broken", current_time)
        ]
        self.mock_cursor.fetchall.return_value = mock_results

        columns = ["issue_id", "user_id", "asset_id", "description", "report_date"]
        query = "SELECT issue_id, user_id, asset_id, description, report_date FROM issues"
        values = ()
        mock_query_builder.return_value = (query, values)

        # Act
        issues = self.issue_repository.fetch_all_issues()

        # Assert
        self.assertEqual(len(issues), 2)
        self.assertEqual(issues[0].issue_id, "ISS001")
        self.assertEqual(issues[0].description, "Screen not working")
        self.assertEqual(issues[1].issue_id, "ISS002")
        self.assertEqual(issues[1].description, "Keyboard broken")
        mock_query_builder.assert_called_once_with("issues", columns=columns)
        self.mock_cursor.execute.assert_called_once_with(query, values)

    @patch("src.app.utils.db.query_builder.GenericQueryBuilder.select")
    def test_fetch_all_issues_empty_list(self, mock_query_builder):
        # Arrange
        self.mock_cursor.fetchall.return_value = []
        columns = ["issue_id", "user_id", "asset_id", "description", "report_date"]
        query = "SELECT issue_id, user_id, asset_id, description, report_date FROM issues"
        values = ()
        mock_query_builder.return_value = (query, values)

        # Act
        issues = self.issue_repository.fetch_all_issues()

        # Assert
        self.assertEqual(len(issues), 0)
        mock_query_builder.assert_called_once_with("issues", columns=columns)
        self.mock_cursor.execute.assert_called_once_with(query, values)

    def test_fetch_all_issues_raises_database_error(self):
        # Arrange
        self.mock_conn.cursor.side_effect = Exception("Database connection error")

        # Act & Assert
        with self.assertRaises(DatabaseError):
            self.issue_repository.fetch_all_issues()

    @patch("src.app.utils.db.query_builder.GenericQueryBuilder.select")
    def test_fetch_user_issues_success(self, mock_query_builder):
        # Arrange
        current_time = datetime.now()
        user_id = "U001"
        mock_results = [
            ("ISS001", "U001", "SN001", "Screen not working", current_time),
            ("ISS002", "U001", "SN002", "Keyboard broken", current_time)
        ]
        self.mock_cursor.fetchall.return_value = mock_results

        columns = ["issue_id", "user_id", "asset_id", "description", "report_date"]
        where_clause = {"user_id": user_id}
        query = "SELECT issue_id, user_id, asset_id, description, report_date FROM issues WHERE user_id = ?"
        values = (user_id,)
        mock_query_builder.return_value = (query, values)

        # Act
        issues = self.issue_repository.fetch_user_issues(user_id)

        # Assert
        self.assertEqual(len(issues), 2)
        self.assertEqual(issues[0].issue_id, "ISS001")
        self.assertEqual(issues[0].user_id, "U001")
        self.assertEqual(issues[1].issue_id, "ISS002")
        self.assertEqual(issues[1].user_id, "U001")
        mock_query_builder.assert_called_once_with("issues", columns=columns, where=where_clause)
        self.mock_cursor.execute.assert_called_once_with(query, values)

    @patch("src.app.utils.db.query_builder.GenericQueryBuilder.select")
    def test_fetch_user_issues_no_issues_found(self, mock_query_builder):
        # Arrange
        user_id = "U999"
        self.mock_cursor.fetchall.return_value = []

        columns = ["issue_id", "user_id", "asset_id", "description", "report_date"]
        where_clause = {"user_id": user_id}
        query = "SELECT issue_id, user_id, asset_id, description, report_date FROM issues WHERE user_id = ?"
        values = (user_id,)
        mock_query_builder.return_value = (query, values)

        # Act
        issues = self.issue_repository.fetch_user_issues(user_id)

        # Assert
        self.assertEqual(len(issues), 0)
        mock_query_builder.assert_called_once_with("issues", columns=columns, where=where_clause)
        self.mock_cursor.execute.assert_called_once_with(query, values)

    def test_fetch_user_issues_raises_database_error(self):
        # Arrange
        user_id = "U001"
        self.mock_conn.cursor.side_effect = Exception("Database connection error")

        # Act & Assert
        with self.assertRaises(DatabaseError):
            self.issue_repository.fetch_user_issues(user_id)