import sqlite3
from typing import List

from AssetManagement.src.app.config.config import DB
from AssetManagement.src.app.models.issue import Issue
from AssetManagement.src.app.utils.errors.error import DatabaseError
from AssetManagement.src.app.utils.db.query_builder import GenericQueryBuilder


class IssueRepository:
    def __init__(self, database: DB):
        self.db = database

    def report_issue(self, issue: Issue) -> None:
        """Reports an issue for a specific asset."""
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            with conn:
                issue_data = {
                    "issue_id": issue.issue_id,
                    "user_id": issue.user_id,
                    "asset_id": issue.asset_id,
                    "description": issue.description,
                    "report_date": issue.report_date
                }
                query, values = GenericQueryBuilder.insert("issues", issue_data)
                cursor.execute(query, values)
        except sqlite3.IntegrityError as e:
            raise DatabaseError(f"Issue reporting failed: {str(e)}")
        except Exception as e:
            raise DatabaseError(f"Unexpected error during issue reporting: {str(e)}")

    def fetch_all_issues(self) -> List[Issue]:
        """Retrieves all issues reported by all users."""
        try:
            conn = self.db.get_connection()
            with conn:
                cursor = conn.cursor()
                columns = ["issue_id", "user_id", "asset_id", "description", "report_date"]
                query, values = GenericQueryBuilder.select("issues", columns=columns)
                cursor.execute(query, values)
                results = cursor.fetchall()

            return [
                Issue(
                    issue_id=row[0],
                    user_id=row[1],
                    asset_id=row[2],
                    description=row[3],
                    report_date=row[4],
                ) for row in results
            ]
        except Exception as e:
            raise DatabaseError(f"Error retrieving user issues: {str(e)}")

    def fetch_user_issues(self, user_id: str) -> List[Issue]:
        """Retrieves all issues reported by specific user."""
        try:
            conn = self.db.get_connection()
            with conn:
                cursor = conn.cursor()
                columns = ["issue_id", "user_id", "asset_id", "description", "report_date"]
                where_clause = {"user_id": user_id}
                query, values = GenericQueryBuilder.select(
                    "issues",
                    columns=columns,
                    where=where_clause
                )
                cursor.execute(query, values)
                results = cursor.fetchall()

            return [
                Issue(
                    issue_id=row[0],
                    user_id=row[1],
                    asset_id=row[2],
                    description=row[3],
                    report_date=row[4],
                ) for row in results
            ]
        except Exception as e:
            raise DatabaseError(f"Error retrieving user issues: {str(e)}")