import uuid
import pytest
from unittest.mock import Mock, AsyncMock, MagicMock
from fastapi import FastAPI, Request

from src.app.config.custom_error_codes import ErrorCodes
from src.app.models.asset_issue import Issue
from src.app.models.request_objects import ReportIssueRequest
from src.app.utils.errors.error import NotExistsError, NotAssignedError
from src.app.controllers.asset_issue.handlers import IssueHandler


@pytest.fixture
def app():
    """FastAPI application fixture"""
    app = FastAPI()
    return app


@pytest.fixture
def mock_request():
    """Mock FastAPI request fixture with all necessary attributes"""
    mock_req = MagicMock(spec=Request)

    # Mock request attributes
    mock_req.method = "GET"
    mock_req.url.path = "/test"
    mock_req.client.host = "127.0.0.1"
    mock_req.headers = {"content-type": "application/json"}

    class MockState:
        user = {
            "user_id": "test-user",
            "role": "admin"
        }

    mock_req.state = MockState()

    # Mock async methods
    mock_req.body = AsyncMock(return_value=b"{}")
    mock_req.json = AsyncMock(return_value={})

    return mock_req


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
    @pytest.mark.asyncio
    async def test_get_user_issues_success(self, issue_handler, sample_issues):
        valid_user_id = "550e8400-e29b-41d4-a716-446655440000"
        issue_handler.issue_service.get_user_issues.return_value = sample_issues

        response = await issue_handler.get_user_issues(valid_user_id)

        assert response["status_code"] == 200
        assert response["message"] == "User issues fetched successfully"
        assert len(response["data"]) == 2
        assert response["data"][0]["description"] == "First issue"

        issue_handler.issue_service.get_user_issues.assert_called_once_with(valid_user_id)

    @pytest.mark.asyncio
    async def test_get_user_issues_user_not_found(self, issue_handler):
        valid_user_id = str(uuid.uuid4())
        issue_handler.issue_service.get_user_issues.side_effect = NotExistsError("No such user exists")

        response = await issue_handler.get_user_issues(valid_user_id)

        assert response["status_code"] == ErrorCodes.RECORD_NOT_FOUND_ERROR
        assert response["message"] == "No such user exists"

    @pytest.mark.asyncio
    async def test_get_user_issues_database_error(self, issue_handler):
        valid_user_id = "550e8400-e29b-41d4-a716-446655440000"
        issue_handler.issue_service.get_user_issues.side_effect = Exception("Database error")

        response = await issue_handler.get_user_issues(valid_user_id)

        assert response["status_code"] == ErrorCodes.DATABASE_OPERATION_ERROR
        assert response["message"] == "Error fetching user issues"

    @pytest.mark.asyncio
    async def test_get_issues_success(self, issue_handler, sample_issues, mock_request):

        issue_handler.issue_service.get_issues.return_value = sample_issues

        response = await issue_handler.get_issues(request=mock_request)

        assert response["status_code"] == 200
        assert response["message"] == "All issues fetched successfully"
        assert len(response["data"]) == 2

        issue_handler.issue_service.get_issues.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_issues_database_error(self, issue_handler, mock_request):
        issue_handler.issue_service.get_issues.side_effect = Exception("Database error")

        response = await issue_handler.get_issues(mock_request)

        assert response["status_code"] == ErrorCodes.DATABASE_OPERATION_ERROR
        assert response["message"] == "Error fetching all issues"

    @pytest.mark.asyncio
    async def test_report_issue_success(self, issue_handler, mock_request, sample_issue):
        issue_data = ReportIssueRequest(
            asset_id="550e8400-e29b-41d4-a716-446655440000",
            description="Test issue"
        )

        issue_handler.issue_service.report_issue = AsyncMock(return_value=sample_issue)
        response = await issue_handler.report_issue(mock_request, issue_data)

        assert response["status_code"] == 200
        assert response["message"] == "Issue reported successfully"
        assert response["data"]["asset_id"] == issue_data.asset_id
        assert response["data"]["description"] == issue_data.description

        issue_handler.issue_service.report_issue.assert_called_once()

    @pytest.mark.asyncio
    async def test_report_issue_not_assigned_error(self, issue_handler, mock_request):
        issue_data = ReportIssueRequest(
            asset_id="550e8400-e29b-41d4-a716-446655440000",
            description="Test issue"
        )
        issue_handler.issue_service.report_issue.side_effect = NotAssignedError("Asset not assigned")

        response = await issue_handler.report_issue(mock_request, issue_data)

        assert response["status_code"] == ErrorCodes.ASSET_NOT_ASSIGNED_ERROR
        assert response["message"] == "Asset not assigned"

    @pytest.mark.asyncio
    async def test_report_issue_asset_not_found(self, issue_handler, mock_request):
        issue_data = ReportIssueRequest(
            asset_id="550e8400-e29b-41d4-a716-446655440000",
            description="Test issue"
        )
        issue_handler.issue_service.report_issue.side_effect = NotExistsError("Asset not found")

        response = await issue_handler.report_issue(mock_request, issue_data)

        assert response["status_code"] == ErrorCodes.ASSET_NOT_FOUND_ERROR
        assert response["message"] == "Asset not found"

    @pytest.mark.asyncio
    async def test_report_issue_database_error(self, issue_handler, mock_request):
        issue_data = ReportIssueRequest(
            asset_id="550e8400-e29b-41d4-a716-446655440000",
            description="Test issue"
        )
        issue_handler.issue_service.report_issue.side_effect = Exception("Database error")

        response = await issue_handler.report_issue(mock_request, issue_data)

        assert response["status_code"] == ErrorCodes.DATABASE_OPERATION_ERROR
        assert response["message"] == "Unexpected error reporting the issue"
