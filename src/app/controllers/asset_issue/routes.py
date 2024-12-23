from fastapi import APIRouter, Depends, Request
from uuid import UUID

from src.app.controllers.asset_issue.handlers import IssueHandler
from src.app.middleware.middleware import auth_middleware
from src.app.services.asset_issue_service import IssueService
from src.app.models.request_objects import ReportIssueRequest
from src.app.models.asset_issue import Issue


def create_issue_routes(issue_service: IssueService) -> APIRouter:
    router = APIRouter(tags=["issues"])
    issue_handler = IssueHandler.create(issue_service)

    router.dependencies = [Depends(auth_middleware)]

    @router.get("/issues")
    async def get_all_issues(request: Request):
        return await issue_handler.get_issues(request)

    @router.post("/report-issue")
    async def report_issue(request: Request, issue: ReportIssueRequest):
        return await issue_handler.report_issue(request, issue)

    @router.get("/issues/{user_id}")
    async def get_user_issues(user_id: str):
        return await issue_handler.get_user_issues(user_id)

    return router
