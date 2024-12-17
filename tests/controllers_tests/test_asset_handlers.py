import unittest
from unittest.mock import MagicMock
from flask import Flask, g

from src.app.models.asset import Asset
from src.app.models.user import User
from src.app.repositories.asset_repository import AssetRepository
from src.app.services.asset_service import AssetService
from src.app.controllers.asset.handlers import AssetHandler
from src.app.services.user_service import UserService
from src.app.utils.errors.error import AlreadyAssignedError, NotAssignedError


class TestAssetHandler(unittest.TestCase):

    def setUp(self):
        """Set up Flask app and mock services."""
        self.app = Flask(__name__)
        self.app.testing = True
        self.client = self.app.test_client()

        # Mock the AssetService
        self.mock_asset_service = MagicMock(spec=AssetService)
        self.mock_user_service = MagicMock(spec=UserService)
        self.mock_asset_repository = MagicMock(spec=AssetRepository)
        self.asset_handler = AssetHandler.create(self.mock_asset_service)

        # Test data
        self.test_asset = Asset(name="Test Asset", description="Test Description")
        self.valid_asset_payload = {
            "name": "New Asset",
            "description": "Asset description"
        }
        self.invalid_asset_payload = {}

    def test_add_asset_success(self):
        """Test successful addition of an asset."""
        with self.app.test_request_context(method="POST", json=self.valid_asset_payload):
            # Mocking the add_asset method of AssetService
            self.mock_asset_service.add_asset.return_value = self.test_asset

            # Call the add_asset method of AssetHandler
            g.role = 'admin'
            response, status_code = self.asset_handler.add_asset()

            # Assert the response and status code
            self.assertEqual(status_code, 200)
            self.assertEqual(response["message"], "Asset added successfully")
            self.mock_asset_service.add_asset.assert_called_once()

    def test_add_asset_invalid_data(self):
        """Test failure when adding an asset with invalid data."""
        with self.app.test_request_context(method="POST", json=self.invalid_asset_payload):
            # Mock the add_asset method to raise an exception
            self.mock_asset_service.add_asset.side_effect = Exception("Invalid data")

            # Call the add_asset method of AssetHandler
            g.role = 'admin'
            response, status_code = self.asset_handler.add_asset()

            # Assert that the error response is correct
            self.assertEqual(status_code, 500)
            self.assertEqual(response["message"], "Unexpected error during asset creation")

    def test_delete_asset_success(self):
        """Test successful deletion of an asset."""
        with self.app.test_request_context(method="DELETE", json={"asset_id": "12345"}):
            # Mocking the delete_asset method of AssetService
            self.mock_asset_service.delete_asset.return_value = self.test_asset

            # Call the delete_asset method of AssetHandler
            g.role = 'admin'
            response, status_code = self.asset_handler.delete_asset("12345")

            # Assert the response and status code
            self.assertEqual(status_code, 200)
            self.assertEqual(response["message"], "Asset deleted successfully")
            self.mock_asset_service.delete_asset.assert_called_once_with("12345")

    def test_delete_asset_invalid_id(self):
        """Test failure when deleting an asset with an invalid ID."""
        with self.app.test_request_context(method="DELETE", json={"asset_id": "invalid_id"}):
            g.role = 'admin'
            response, status_code = self.asset_handler.delete_asset("invalid_id")

            # Assert the response and status code
            self.assertEqual(status_code, 400)
            self.assertEqual(response["message"], "Invalid asset id")

    def test_assign_asset_success(self):
        """Test successful assignment of an asset."""
        assign_payload = {"user_id": "user123", "asset_id": "asset123"}
        with self.app.test_request_context(method="POST", json=assign_payload):
            # Mocking the assign_asset method of AssetService
            self.mock_asset_service.assign_asset.return_value = None

            # Call the assign_asset method of AssetHandler
            g.role = 'admin'
            response, status_code = self.asset_handler.assign_asset()

            # Assert the response and status code
            self.assertEqual(status_code, 200)
            self.assertEqual(response["message"], "Asset assigned successfully")
            self.mock_asset_service.assign_asset.assert_called_once()

    def test_assign_asset_already_assigned(self):
        """Test failure when assigning an already assigned asset."""
        assign_payload = {"user_id": "user123", "asset_id": "asset123"}
        with self.app.test_request_context(method="POST", json=assign_payload):
            # Mock the assign_asset method to raise AlreadyAssignedError
            self.mock_asset_service.assign_asset.side_effect = AlreadyAssignedError("Asset already assigned")

            # Call the assign_asset method of AssetHandler
            g.role = 'admin'
            response, status_code = self.asset_handler.assign_asset()

            # Assert the response and status code
            self.assertEqual(status_code, 400)
            self.assertEqual(response["message"], "Asset already assigned")

    def test_unassign_asset_success(self):
        """Test successful unassignment of an asset."""
        unassign_payload = {"user_id": "user123", "asset_id": "asset123"}

        dummy_user = User(
            name="pravin",
            email="Pravin123@watchguard.com",
            department="CLOUD PLATFORM",
            password="Password@123"
        )

        dummy_asset = Asset(
            name="Dell x32",
            description="Dell laptop"
        )

        with self.app.test_request_context(method="POST", json=unassign_payload):
            # Mock the unassign_asset method of AssetService
            self.mock_asset_service.unassign_asset.return_value = None
            self.mock_asset_repository.fetch_asset_by_id(unassign_payload['asset_id']).return_value = dummy_asset
            self.mock_user_service.get_user_by_id(unassign_payload['user_id']).return_value = dummy_user
            self.mock_asset_repository.is_asset_assigned(unassign_payload['user_id'],unassign_payload['asset_id']).return_value = True

            # Call the unassign_asset method of AssetHandler
            g.role='admin'
            response, status_code = self.asset_handler.unassign_asset()

            # Assert the response and status code
            self.assertEqual(status_code, 200)
            self.assertEqual(response["message"], "Asset unassigned successfully")
            self.mock_asset_service.unassign_asset.assert_called_once()

    def test_unassign_asset_not_assigned(self):
        """Test failure when unassigning a non-assigned asset."""
        unassign_payload = {"user_id": "user123", "asset_id": "asset123"}
        with self.app.test_request_context(method="POST", json=unassign_payload):
            # Mock the unassign_asset method to raise NotAssignedError
            self.mock_asset_service.unassign_asset.side_effect = NotAssignedError("Asset not assigned")

            # Call the unassign_asset method of AssetHandler
            response, status_code = self.asset_handler.unassign_asset()

            # Assert the response and status code
            self.assertEqual(status_code, 400)
            self.assertEqual(response["message"], "Asset not assigned")

    def test_get_assets_success(self):
        """Test successful retrieval of assets."""
        with self.app.test_request_context(method="GET"):
            # Mock the get_assets method of AssetService
            self.mock_asset_service.get_assets.return_value = [self.test_asset]

            # Call the get_assets method of AssetHandler
            g.role = 'admin'
            response, status_code = self.asset_handler.get_assets()

            # Assert the response and status code
            self.assertEqual(status_code, 200)
            self.assertEqual(response["message"], "Assets retrieved successfully")
            self.assertEqual(len(response["data"]), 1)
            self.mock_asset_service.get_assets.assert_called_once()

