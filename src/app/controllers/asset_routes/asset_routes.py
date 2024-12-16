from flask import Blueprint

from src.app.controllers.asset_routes.asset_handlers import AssetHandler
from src.app.controllers.issue_routes.issue_handlers import IssueHandler
from src.app.middleware.middleware import auth_middleware
from src.app.services.asset_service import AssetService
from src.app.services.issue_service import IssueService


def create_asset_routes(asset_service: AssetService) -> Blueprint:
    asset_routes_blueprint = Blueprint('asset_routes', __name__)
    asset_routes_blueprint.before_request(auth_middleware)
    asset_handler = AssetHandler.create(asset_service)
    # asset-related routes
    asset_routes_blueprint.add_url_rule(
        '/assets', 'assets', asset_handler.get_assets, methods=['GET']
    )

    asset_routes_blueprint.add_url_rule(
        '/add-asset', 'add-asset', asset_handler.add_asset, methods=['POST']
    )

    asset_routes_blueprint.add_url_rule(
        '/delete-asset/<asset_id>', 'delete_asset', asset_handler.delete_asset, methods=['DELETE']
    )

    asset_routes_blueprint.add_url_rule(
        '/assign-asset', 'assign-asset', asset_handler.assign_asset, methods=['POST']
    )

    asset_routes_blueprint.add_url_rule(
        '/unassign-asset', 'unassign_asset', asset_handler.unassign_asset, methods=['POST']
    )

    asset_routes_blueprint.add_url_rule(
        '/assigned-assets/<user_id>', 'assigned_assets', asset_handler.assigned_assets, methods=['GET']
    )

    asset_routes_blueprint.add_url_rule(
        '/assigned-assets/all', 'all_assigned_assets', asset_handler.assigned_all_assets, methods=['GET']
    )

    return asset_routes_blueprint
