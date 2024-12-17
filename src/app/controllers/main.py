from flask import Flask

from src.app.controllers.asset.routes import create_asset_routes
from src.app.controllers.asset_issue.routes import create_issue_routes
from src.app.controllers.users.routes import create_user_routes
from src.app.repositories.asset_repository import AssetRepository
from src.app.repositories.asset_issue_repository import IssueRepository
from src.app.repositories.user_repository import UserRepository
from src.app.services.asset_service import AssetService
from src.app.services.asset_issue_service import IssueService
from src.app.services.user_service import UserService
from src.app.utils.db.db import DB


def create_app():
    app = Flask(__name__)

    db = DB()

    user_repository = UserRepository(db)
    issue_repository = IssueRepository(db)
    asset_repository = AssetRepository(db)

    user_service = UserService(user_repository)
    asset_service = AssetService(asset_repository, user_service)
    issue_service = IssueService(issue_repository, asset_service, user_service)

    # Register blueprints
    app.register_blueprint(
        create_user_routes(user_service)
    )

    app.register_blueprint(
        create_issue_routes(issue_service)
    )

    app.register_blueprint(
        create_asset_routes(asset_service)
    )

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
