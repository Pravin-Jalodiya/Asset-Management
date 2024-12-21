from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.app.controllers.asset.routes import create_asset_routes
from src.app.controllers.asset_issue.routes import create_issue_routes
from src.app.controllers.users.routes import create_user_routes, create_auth_routes
from src.app.middleware.middleware import auth_middleware
from src.app.repositories.asset_repository import AssetRepository
from src.app.repositories.asset_issue_repository import IssueRepository
from src.app.repositories.user_repository import UserRepository
from src.app.services.asset_service import AssetService
from src.app.services.asset_issue_service import IssueService
from src.app.services.user_service import UserService
from src.app.utils.db.db import DB
from src.app.utils.logger.logger import LoggerMiddleware


def create_app():
    app = FastAPI(title="Asset Management API")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"]
    )

    app.add_middleware(LoggerMiddleware)

    db = DB()

    user_repository = UserRepository(db)
    issue_repository = IssueRepository(db)
    asset_repository = AssetRepository(db)

    user_service = UserService(user_repository)
    asset_service = AssetService(asset_repository, user_service)
    issue_service = IssueService(issue_repository, asset_service, user_service)

    # Include routers
    app.include_router(create_auth_routes(user_service))
    app.include_router(create_user_routes(user_service))
    app.include_router(create_issue_routes(issue_service))
    app.include_router(create_asset_routes(asset_service))

    return app


if __name__ == "__main__":
    import uvicorn
    app = create_app()
    uvicorn.run(app, host="127.0.0.1", port=5000)
