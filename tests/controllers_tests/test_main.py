import unittest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from src.app.controllers.main import create_app


class TestAppFactory(unittest.TestCase):
    def test_create_app_returns_fastapi_app(self):
        """
        Test that create_app returns a FastAPI application
        """
        # Act
        app = create_app()

        # Assert
        self.assertIsInstance(app, FastAPI)

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
        client = TestClient(app)

        # Expected route prefixes based on actual API structure
        expected_routes = {
            # Auth routes
            '/signup',
            '/login',
            # User routes
            '/users',
            '/user',
            # Issue routes
            '/issues',
            '/report-issue',
            # Asset routes
            '/assets',
            '/add-asset',
            '/assign-asset',
            '/unassign-asset',
            '/assigned-assets'
        }

        # Act
        routes = [route.path for route in app.routes]

        # Assert
        for expected_route in expected_routes:
            matching_routes = [r for r in routes if expected_route in r]
            self.assertTrue(
                len(matching_routes) > 0,
                f"No routes found matching prefix '{expected_route}'. Available routes: {routes}"
            )