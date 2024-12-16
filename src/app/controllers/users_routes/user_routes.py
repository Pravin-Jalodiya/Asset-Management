from flask import Blueprint

from src.app.controllers.users_routes.user_handlers import UserHandler
from src.app.middleware.middleware import auth_middleware
from src.app.services.user_service import UserService


def create_user_routes(user_service: UserService) -> Blueprint:
    user_routes_blueprint = Blueprint('user_routes', __name__)
    user_routes_blueprint.before_request(auth_middleware)
    user_handler = UserHandler.create(user_service)

    # Authentication routes
    user_routes_blueprint.add_url_rule(
        '/login', 'login', user_handler.login, methods=['POST']
    )
    user_routes_blueprint.add_url_rule(
        '/signup', 'signup', user_handler.signup, methods=['POST']
    )

    # User related routes
    user_routes_blueprint.add_url_rule(
        '/users', 'users', user_handler.get_users, methods=['GET']
    )

    user_routes_blueprint.add_url_rule(
        '/user/<user_id>', 'user', user_handler.get_user, methods=['GET']
    )

    user_routes_blueprint.add_url_rule(
        '/delete-user/<user_id>', 'delete_user', user_handler.delete_user, methods=['DELETE']
    )

    return user_routes_blueprint
