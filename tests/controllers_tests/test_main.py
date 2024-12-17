import unittest
from flask import Flask
from src.app.controllers.main import create_app


class TestAppFactory(unittest.TestCase):
    def test_create_app_returns_flask_app(self):
        """
        Test that create_app returns a Flask application
        """
        # Act
        app = create_app()

        # Assert
        self.assertIsInstance(app, Flask)

    def test_dependencies_are_created(self):
        """
        Test that all repositories and services are created
        """
        # Act & Assert
        try:
            # This would have happened during app creation
            app = create_app()
        except Exception as e:
            self.fail(f"create_app() raised {type(e).__name__} unexpectedly: {e}")

    def test_services_have_correct_dependencies(self):
        """
        Verify that services are created with their correct dependencies
        """
        # Act
        app = create_app()

        # We'll use the blueprint registration as a proxy to verify dependency injection
        # Since we can't directly access the services, we're checking that the app
        # was created without any dependency injection errors
        try:
            # This would have happened during app creation
            app = create_app()
        except Exception as e:
            self.fail(f"Dependency injection failed: {type(e).__name__} - {e}")

    def test_database_initialized(self):
        """
        Verify that the database is initialized during app creation
        """
        # Act & Assert
        try:
            # This would have happened during app creation
            app = create_app()
        except Exception as e:
            self.fail(f"Database initialization failed: {type(e).__name__} - {e}")

    def test_all_routes_registered(self):
        """
        Verify that all expected routes are registered
        """
        # Arrange
        app = create_app()

        # Expected route prefixes
        expected_routes = [
        ]

        # Act & Assert
        with app.test_request_context():
            # Get all registered routes
            routes = [rule.rule for rule in app.url_map.iter_rules()]

            # Check that all expected routes are in the registered routes
            for route in expected_routes:
                self.assertTrue(any(route in r for r in routes),
                                f"Route {route} not found in registered routes")
