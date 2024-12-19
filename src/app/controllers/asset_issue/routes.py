from fastapi import APIRouter, Depends, HTTPException, Path, Query
from typing import List, Optional
from uuid import UUID

from src.app.controllers.asset_issue.handlers import IssueHandler
from src.app.middleware.middleware import auth_middleware
from src.app.services.asset_issue_service import IssueService
from src.app.models.request_objects import ReportIssueRequest
from src.app.models.asset_issue import Issue

def create_issue_routes(issue_service: IssueService) -> APIRouter:
    router = APIRouter(prefix="/issues", tags=["issues"])
    issue_handler = IssueHandler.create(issue_service)

    @router.get(
        "/user/{user_id}",
        response_model=dict,
        summary="Get issues reported by a specific user",
        description="Retrieves all issues reported by the specified user ID"
    )
    async def get_user_issues(
        user_id: UUID = Path(..., description="The ID of the user to get issues for"),
        _: dict = Depends(auth_middleware)
    ):
        return await issue_handler.get_user_issues(str(user_id))

    @router.get(
        "/",
        response_model=dict,
        summary="Get all issues",
        description="Retrieves all reported issues. Requires admin access."
    )
    async def get_all_issues(
        status: Optional[str] = Query(
            None,
            description="Filter issues by status (e.g., 'OPEN', 'CLOSED')"
        ),
        _: dict = Depends(auth_middleware)
    ):
        return await issue_handler.get_issues()

    @router.post(
        "/report",
        response_model=dict,
        summary="Report a new issue",
        description="Report a new issue for an asset"
    )
    async def report_issue(
        issue: ReportIssueRequest,
        _: dict = Depends(auth_middleware)
    ):
        return await issue_handler.report_issue(issue)

    @router.patch(
        "/{issue_id}/status",
        response_model=dict,
        summary="Update issue status",
        description="Update the status of an existing issue. Requires admin access."
    )
    async def update_issue_status(
        issue_id: UUID = Path(..., description="The ID of the issue to update"),
        status: str = Query(..., description="New status for the issue"),
        _: dict = Depends(auth_middleware)
    ):
        return await issue_handler.update_issue_status(str(issue_id), status)

    @router.get(
        "/{issue_id}",
        response_model=dict,
        summary="Get issue details",
        description="Get detailed information about a specific issue"
    )
    async def get_issue(
        issue_id: UUID = Path(..., description="The ID of the issue to retrieve"),
        _: dict = Depends(auth_middleware)
    ):
        return await issue_handler.get_issue(str(issue_id))

    return router
