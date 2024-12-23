import uuid
import pytest
from unittest.mock import Mock
from fastapi import Request

from src.app.controllers.asset_issue.handlers import IssueHandler
from src.app.models.asset_issue import Issue
from src.app.models.request_objects import ReportIssueRequest
from src.app.utils.errors.error import NotExistsError, NotAssignedError
from src.app.config.custom_error_codes import ErrorCodes


@pytest.fixture
def mock_request():
    """Mock FastAPI request fixture with user context"""
    mock_scope = {
        "type": "http",
        "headers": [],
        "method": "GET",
        "path": "/",
        "query_string": b"",
        "client": ("127.0.0.1", 8000),
    }

    async def mock_receive():
        return {"type": "http.request", "body": b""}

    mock_request = Request(mock_scope, receive=mock_receive)
    mock_request.state.user = {"role": "user", "user_id": str(uuid.uuid4())}
    return mock_request


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
    issue = Issue(
        asset_id=str(uuid.uuid4()),
        description="Test issue description"
    )
    issue.id = str(uuid.uuid4())
    issue.user_id = str(uuid.uuid4())
    issue.status = "PENDING"
    return issue


@pytest.fixture
def sample_issues():
    """Sample list of issues fixture"""
    issues = []
    for i in range(2):
        issue = Issue(
            asset_id=str(uuid.uuid4()),
            description=f"Test issue {i+1}"
        )
        issue.id = str(uuid.uuid4())
        issue.user_id = str(uuid.uuid4())
        issue.status = "PENDING"
        issues.append(issue)
    return issues


class TestIssueHandler:
    @pytest.mark.asyncio
    async def test_get_user_issues_success(self, issue_handler, sample_issues):
        user_id = str(uuid.uuid4())
        issue_handler.issue_service.get_user_issues.return_value = sample_issues

        response = await issue_handler.get_user_issues(user_id)

        assert response["status_code"] == 200
        assert response["message"] == "User issues fetched successfully"
        assert len(response["data"]) == 2
        assert all(isinstance(issue["id"], str) for issue in response["data"])
        issue_handler.issue_service.get_user_issues.assert_called_once_with(user_id)

    @pytest.mark.asyncio
    async def test_get_user_issues_user_not_found(self, issue_handler):
        user_id = str(uuid.uuid4())
        issue_handler.issue_service.get_user_issues.side_effect = NotExistsError("No such user exists")

        response = await issue_handler.get_user_issues(user_id)

        assert response["status_code"] == ErrorCodes.RECORD_NOT_FOUND_ERROR.value
        assert response["message"] == "No such user exists"

    @pytest.mark.asyncio
    async def test_get_user_issues_database_error(self, issue_handler):
        user_id = str(uuid.uuid4())
        issue_handler.issue_service.get_user_issues.side_effect = Exception("Database error")

        response = await issue_handler.get_user_issues(user_id)
        response_body = response.body.decode()
        import json
        response_data = json.loads(response_body)

        assert response.status_code == 500
        assert response_data["status_code"] == ErrorCodes.DATABASE_OPERATION_ERROR.value
        assert response_data["message"] == "Error fetching user issues"

    @pytest.mark.asyncio
    async def test_get_issues_success(self, issue_handler, mock_request, sample_issues):
        # Set admin role for this test
        mock_request.state.user["role"] = "admin"
        
        issue_handler.issue_service.get_issues.return_value = sample_issues

        response = await issue_handler.get_issues(mock_request)

        assert response["status_code"] == 200
        assert response["message"] == "All issues fetched successfully"
        assert len(response["data"]) == 2
        assert all(isinstance(issue["id"], str) for issue in response["data"])

    @pytest.mark.asyncio
    async def test_get_issues_database_error(self, issue_handler, mock_request):
        # Set admin role for this test
        mock_request.state.user["role"] = "admin"
        
        issue_handler.issue_service.get_issues.side_effect = Exception("Database error")

        response = await issue_handler.get_issues(mock_request)
        response_body = response.body.decode()
        import json
        response_data = json.loads(response_body)

        assert response.status_code == 500
        assert response_data["status_code"] == ErrorCodes.DATABASE_OPERATION_ERROR.value
        assert response_data["message"] == "Error fetching all issues"

    @pytest.mark.asyncio
    async def test_report_issue_success(self, issue_handler, mock_request, sample_issue):
        issue_data = ReportIssueRequest(
            asset_id=str(uuid.uuid4()),
            description="Test issue description"
        )

        # Set the user_id in the sample_issue to match the request context
        sample_issue.user_id = mock_request.state.user["user_id"]
        issue_handler.issue_service.report_issue.return_value = sample_issue
        
        response = await issue_handler.report_issue(mock_request, issue_data)

        assert response["status_code"] == 200
        assert response["message"] == "Issue reported successfully"
        assert response["data"]["description"] == issue_data.description
        assert "issue_id" in response["data"]
        assert response["data"]["report_date"] is not None
        assert response["data"]["asset_id"] is not None

    @pytest.mark.asyncio
    async def test_report_issue_not_assigned_error(self, issue_handler, mock_request):
        issue_data = ReportIssueRequest(
            asset_id=str(uuid.uuid4()),
            description="Test issue description"
        )
        issue_handler.issue_service.report_issue.side_effect = NotAssignedError("Asset not assigned")

        response = await issue_handler.report_issue(mock_request, issue_data)

        assert response["status_code"] == ErrorCodes.ASSET_NOT_ASSIGNED_ERROR.value
        assert response["message"] == "Asset not assigned"

    @pytest.mark.asyncio
    async def test_report_issue_asset_not_found(self, issue_handler, mock_request):
        issue_data = ReportIssueRequest(
            asset_id=str(uuid.uuid4()),
            description="Test issue description"
        )
        issue_handler.issue_service.report_issue.side_effect = NotExistsError("Asset not found")

        response = await issue_handler.report_issue(mock_request, issue_data)

        assert response["status_code"] == ErrorCodes.ASSET_NOT_FOUND_ERROR.value
        assert response["message"] == "Asset not found"

    @pytest.mark.asyncio
    async def test_report_issue_database_error(self, issue_handler, mock_request):
        issue_data = ReportIssueRequest(
            asset_id=str(uuid.uuid4()),
            description="Test issue description"
        )
        issue_handler.issue_service.report_issue.side_effect = Exception("Database error")

        response = await issue_handler.report_issue(mock_request, issue_data)
        response_body = response.body.decode()
        import json
        response_data = json.loads(response_body)

        assert response.status_code == 500
        assert response_data["status_code"] == ErrorCodes.DATABASE_OPERATION_ERROR.value
        assert response_data["message"] == "Unexpected error reporting the issue"
