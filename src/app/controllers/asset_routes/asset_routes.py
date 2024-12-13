from flask import Blueprint

from AssetManagement.src.app.controllers.issue_routes.issue_handlers import IssueHandler
from AssetManagement.src.app.middleware.middleware import auth_middleware
from AssetManagement.src.app.services.asset_service import AssetService
from AssetManagement.src.app.services.issue_service import IssueService


def create_issue_routes(asset_service: AssetService) -> Blueprint:
    asset_routes_blueprint = Blueprint('asset_routes', __name__)
    asset_routes_blueprint.before_request(auth_middleware)
    asset_handler = assetHandler.create(asset_service)
    # asset-related routes
    asset_routes_blueprint.add_url_rule(
        '/report-asset', 'report_asset', asset_handler.report_asset, methods=['POST']
    )

    asset_routes_blueprint.add_url_rule(
        '/assets/<user_id>', 'get_user_assets', asset_handler.get_user_assets, methods=['GET']
    )

    asset_routes_blueprint.add_url_rule(
        '/assets', 'get_assets', asset_handler.get_assets, methods=['GET']
    )

    return asset_routes_blueprint