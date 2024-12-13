from flask import Flask

from AssetManagement.src.app.controllers.issue_routes.issue_routes import create_issue_routes
from AssetManagement.src.app.controllers.users_routes.user_routes import create_user_routes
from AssetManagement.src.app.repositories.asset_repository import AssetRepository
from AssetManagement.src.app.repositories.issue_repository import IssueRepository
from AssetManagement.src.app.repositories.user_repository import UserRepository
from AssetManagement.src.app.services.asset_service import AssetService
from AssetManagement.src.app.services.issue_service import IssueService
from AssetManagement.src.app.services.user_service import UserService
from AssetManagement.src.app.utils.db.db import DB


def create_app():
    app = Flask(__name__)

    db = DB()

    user_repository = UserRepository(db)
    issue_repository = IssueRepository(db)
    asset_repository = AssetRepository(db)

    user_service = UserService(user_repository)
    asset_service = AssetService(asset_repository, user_service)
    issue_service = IssueService(issue_repository)


    # Register blueprints
    app.register_blueprint(
        create_user_routes(user_service)
    )

    app.register_blueprint(
        create_issue_routes(issue_service)
    )

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)