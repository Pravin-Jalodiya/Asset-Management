import unittest
import uuid
from unittest.mock import MagicMock
from flask import Flask, g
from werkzeug.routing import ValidationError

from src.app.config.custom_error_codes import ErrorCodes
from src.app.models.asset import Asset
from src.app.repositories.asset_repository import AssetRepository
from src.app.services.asset_service import AssetService
from src.app.controllers.asset.handlers import AssetHandler
from src.app.services.user_service import UserService
from src.app.utils.errors.error import AlreadyAssignedError, NotAssignedError, DatabaseError, NotExistsError


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
        asset_id = str(uuid.uuid4())
        with self.app.test_request_context(method="DELETE", json={"asset_id": asset_id}):
            # Mocking the delete_asset method of AssetService
            self.mock_asset_service.delete_asset.return_value = self.test_asset

            # Call the delete_asset method of AssetHandler
            g.role = 'admin'
            response, status_code = self.asset_handler.delete_asset(asset_id)

            # Assert the response and status code
            self.assertEqual(status_code, 200)
            self.assertEqual(response["message"], "Asset deleted successfully")
            self.mock_asset_service.delete_asset.assert_called_once_with(asset_id)

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
        user_id = str(uuid.uuid4())
        asset_id = str(uuid.uuid4())
        assign_payload = {"user_id": user_id, "asset_id": asset_id}
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
        user_id = str(uuid.uuid4())
        asset_id = str(uuid.uuid4())
        assign_payload = {"user_id": user_id, "asset_id": asset_id}
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
        user_id = str(uuid.uuid4())
        asset_id = str(uuid.uuid4())
        unassign_payload = {"user_id": user_id, "asset_id": asset_id}

        with self.app.test_request_context(method="POST", json=unassign_payload):
            # Ensure g.role is set
            g.role = 'admin'

            response, status_code = self.asset_handler.unassign_asset()

            # Assert the response and status code
            self.assertEqual(status_code, 200)
            self.assertEqual(response["message"], "Asset unassigned successfully")


    def test_unassign_asset_not_assigned(self):
        """Test failure when unassigning a non-assigned asset."""
        user_id = str(uuid.uuid4())
        asset_id = str(uuid.uuid4())
        unassign_payload = {"user_id": user_id, "asset_id": asset_id}
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

    def test_unassign_asset_not_exists_error(self):
        """Test unassignment when user or asset does not exist."""
        user_id = str(uuid.uuid4())
        asset_id = str(uuid.uuid4())
        unassign_payload = {"user_id": user_id, "asset_id": asset_id}

        with self.app.test_request_context(method="POST", json=unassign_payload):
            # Mock the unassign_asset method to raise NotExistsError
            self.mock_asset_service.unassign_asset.side_effect = NotExistsError("User or asset not found")

            # Call the unassign_asset method of AssetHandler
            response, status_code = self.asset_handler.unassign_asset()

            # Assert the response and status code
            self.assertEqual(status_code, 400)
            self.assertEqual(response["status_code"], ErrorCodes.RECORD_NOT_FOUND_ERROR)
            self.assertEqual(response["message"], "User or asset not found")

    def test_unassign_asset_validation_error(self):
        """Test unassignment with invalid input."""
        invalid_payloads = [
            {"user_id": str(uuid.uuid4()), "asset_id": str(uuid.uuid4())},
            {"user_id": str(uuid.uuid4()), "asset_id": str(uuid.uuid4())},
        ]

        for unassign_payload in invalid_payloads:
            with self.app.test_request_context(method="POST", json=unassign_payload):
                # Mock the unassign_asset method to raise ValidationError
                self.mock_asset_service.unassign_asset.side_effect = ValidationError("Invalid input")

                # Call the unassign_asset method of AssetHandler
                response, status_code = self.asset_handler.unassign_asset()

                # Assert the response and status code
                self.assertEqual(status_code, 400)
                self.assertEqual(response["status_code"], ErrorCodes.VALIDATION_ERROR)
                self.assertEqual(response["message"], "Invalid input")

    def test_unassign_asset_not_assigned_error(self):
        """Test unassignment when asset is not assigned."""
        user_id = str(uuid.uuid4())
        asset_id = str(uuid.uuid4())
        unassign_payload = {"user_id": user_id, "asset_id": asset_id}

        with self.app.test_request_context(method="POST", json=unassign_payload):
            # Mock the unassign_asset method to raise NotAssignedError
            self.mock_asset_service.unassign_asset.side_effect = NotAssignedError("Asset is not assigned")

            # Call the unassign_asset method of AssetHandler
            response, status_code = self.asset_handler.unassign_asset()

            # Assert the response and status code
            self.assertEqual(status_code, 400)
            self.assertEqual(response["status_code"], ErrorCodes.ASSET_NOT_ASSIGNED_ERROR)
            self.assertEqual(response["message"], "Asset is not assigned")

    def test_unassign_asset_database_error(self):
        """Test unassignment with database error."""
        user_id = str(uuid.uuid4())
        asset_id = str(uuid.uuid4())
        unassign_payload = {"user_id": user_id, "asset_id": asset_id}

        with self.app.test_request_context(method="POST", json=unassign_payload):
            # Mock the unassign_asset method to raise DatabaseError
            self.mock_asset_service.unassign_asset.side_effect = DatabaseError("Database operation failed")

            # Call the unassign_asset method of AssetHandler
            response, status_code = self.asset_handler.unassign_asset()

            # Assert the response and status code
            self.assertEqual(status_code, 500)
            self.assertEqual(response["status_code"], ErrorCodes.DATABASE_OPERATION_ERROR)
            self.assertEqual(response["message"], "Error unassigning asset")

    def test_unassign_asset_unexpected_error(self):
        """Test unassignment with an unexpected error."""
        user_id = str(uuid.uuid4())
        asset_id = str(uuid.uuid4())
        unassign_payload = {"user_id": user_id, "asset_id": asset_id}

        with self.app.test_request_context(method="POST", json=unassign_payload):
            # Mock the unassign_asset method to raise an unexpected exception
            self.mock_asset_service.unassign_asset.side_effect = Exception("Unexpected error")

            # Call the unassign_asset method of AssetHandler
            response, status_code = self.asset_handler.unassign_asset()

            # Assert the response and status code
            self.assertEqual(status_code, 500)
            self.assertEqual(response["status_code"], ErrorCodes.DATABASE_OPERATION_ERROR)
            self.assertEqual(response["message"], "Error unassigning asset")

    def test_delete_asset_invalid_uuid(self):
        """Test deletion with invalid UUID."""
        invalid_asset_ids = [
            "invalid-uuid",
            "",
            "12345"
        ]

        for asset_id in invalid_asset_ids:
            with self.app.test_request_context(method="DELETE", json={"asset_id": asset_id}):
                # Ensure g.role is set for admin access
                g.role = 'admin'

                response, status_code = self.asset_handler.delete_asset(asset_id)

                # Assert the response and status code
                self.assertEqual(status_code, 400)
                self.assertEqual(response["status_code"], ErrorCodes.VALIDATION_ERROR)
                self.assertEqual(response["message"], "Invalid asset id")

    def test_delete_asset_not_exists(self):
        """Test deletion of non-existent asset."""
        asset_id = str(uuid.uuid4())

        with self.app.test_request_context(method="DELETE", json={"asset_id": asset_id}):
            # Mock the delete_asset method to raise NotExistsError
            self.mock_asset_service.delete_asset.side_effect = NotExistsError("Asset not found")

            # Ensure g.role is set for admin access
            g.role = 'admin'

            response, status_code = self.asset_handler.delete_asset(asset_id)

            # Assert the response and status code
            self.assertEqual(status_code, 404)
            self.assertEqual(response["status_code"], ErrorCodes.RECORD_NOT_FOUND_ERROR)
            self.assertEqual(response["message"], "Asset not found")

    def test_delete_asset_database_error(self):
        """Test deletion with database error."""
        asset_id = str(uuid.uuid4())

        with self.app.test_request_context(method="DELETE", json={"asset_id": asset_id}):
            # Mock the delete_asset method to raise DatabaseError
            self.mock_asset_service.delete_asset.side_effect = DatabaseError("Database error")

            # Ensure g.role is set for admin access
            g.role = 'admin'

            response, status_code = self.asset_handler.delete_asset(asset_id)

            # Assert the response and status code
            self.assertEqual(status_code, 500)
            self.assertEqual(response["status_code"], ErrorCodes.DATABASE_OPERATION_ERROR)
            self.assertEqual(response["message"], "Error deleting asset")

    def test_delete_asset_unexpected_error(self):
        """Test deletion with unexpected error."""
        asset_id = str(uuid.uuid4())

        with self.app.test_request_context(method="DELETE", json={"asset_id": asset_id}):
            # Mock the delete_asset method to raise an unexpected exception
            self.mock_asset_service.delete_asset.side_effect = Exception("Unexpected error")

            # Ensure g.role is set for admin access
            g.role = 'admin'

            response, status_code = self.asset_handler.delete_asset(asset_id)

            # Assert the response and status code
            self.assertEqual(status_code, 500)
            self.assertEqual(response["status_code"], ErrorCodes.DATABASE_OPERATION_ERROR)
            self.assertEqual(response["message"], "Error deleting asset")

    def test_assigned_assets_success(self):
        """Test successful retrieval of assigned assets for a user."""
        user_id = str(uuid.uuid4())
        dummy_assets = [
            {"id": str(uuid.uuid4()), "name": "Asset 1"},
            {"id": str(uuid.uuid4()), "name": "Asset 2"}
        ]

        with self.app.test_request_context(method="GET"):
            # Mock the view_assigned_assets method to return dummy assets
            self.mock_asset_service.view_assigned_assets.return_value = dummy_assets

            response, status_code = self.asset_handler.assigned_assets(user_id)

            # Assert the response and status code
            self.assertEqual(status_code, 200)
            self.assertEqual(response["message"], "Assigned assets retrieved successfully")
            self.assertEqual(len(response["data"]), 2)
            self.mock_asset_service.view_assigned_assets.assert_called_once_with(user_id)

    def test_assigned_assets_invalid_uuid(self):
        """Test assigned assets retrieval with invalid UUID."""
        invalid_user_ids = [
            "invalid-uuid",
            "",
            "12345"
        ]

        for user_id in invalid_user_ids:
            with self.app.test_request_context(method="GET"):
                response, status_code = self.asset_handler.assigned_assets(user_id)

                # Assert the response and status code
                self.assertEqual(status_code, 200)
                self.assertEqual(response["status_code"], ErrorCodes.VALIDATION_ERROR)
                self.assertEqual(response["message"], "Invalid user id")

    def test_assigned_assets_not_exists(self):
        """Test assigned assets retrieval for non-existent user."""
        user_id = str(uuid.uuid4())

        with self.app.test_request_context(method="GET"):
            # Mock the view_assigned_assets method to raise NotExistsError
            self.mock_asset_service.view_assigned_assets.side_effect = NotExistsError("User not found")

            response, status_code = self.asset_handler.assigned_assets(user_id)

            # Assert the response and status code
            self.assertEqual(status_code, 400)
            self.assertEqual(response["status_code"], ErrorCodes.RECORD_NOT_FOUND_ERROR)
            self.assertEqual(response["message"], "User not found")

    def test_assigned_assets_database_error(self):
        """Test assigned assets retrieval with database error."""
        user_id = str(uuid.uuid4())

        with self.app.test_request_context(method="GET"):
            # Mock the view_assigned_assets method to raise DatabaseError
            self.mock_asset_service.view_assigned_assets.side_effect = DatabaseError("Database error")

            response, status_code = self.asset_handler.assigned_assets(user_id)

            # Assert the response and status code
            self.assertEqual(status_code, 500)
            self.assertEqual(response["status_code"], ErrorCodes.DATABASE_OPERATION_ERROR)
            self.assertEqual(response["message"], "Error fetching assigned assets")

    def test_assigned_all_assets_success(self):
        """Test successful retrieval of all assigned assets."""
        dummy_assets = [
            {"id": str(uuid.uuid4()), "name": "Asset 1", "user_id": str(uuid.uuid4())},
            {"id": str(uuid.uuid4()), "name": "Asset 2", "user_id": str(uuid.uuid4())}
        ]

        with self.app.test_request_context(method="GET"):
            # Ensure g.role is set for admin access
            g.role = 'admin'

            # Mock the view_all_assigned_assets method to return dummy assets
            self.mock_asset_service.view_all_assigned_assets.return_value = dummy_assets

            response, status_code = self.asset_handler.assigned_all_assets()

            # Assert the response and status code
            self.assertEqual(status_code, 200)
            self.assertEqual(response["message"], "All assigned assets retrieved successfully")
            self.assertEqual(len(response["data"]), 2)
            self.mock_asset_service.view_all_assigned_assets.assert_called_once()

    def test_assigned_all_assets_database_error(self):
        """Test all assigned assets retrieval with database error."""
        with self.app.test_request_context(method="GET"):
            # Ensure g.role is set for admin access
            g.role = 'admin'

            # Mock the view_all_assigned_assets method to raise DatabaseError
            self.mock_asset_service.view_all_assigned_assets.side_effect = DatabaseError("Database error")

            response, status_code = self.asset_handler.assigned_all_assets()

            # Assert the response and status code
            self.assertEqual(status_code, 500)
            self.assertEqual(response["status_code"], ErrorCodes.DATABASE_OPERATION_ERROR)
            self.assertEqual(response["message"], "Error fetching assigned assets")

    def test_assigned_all_assets_unexpected_error(self):
        """Test all assigned assets retrieval with unexpected error."""
        with self.app.test_request_context(method="GET"):
            # Ensure g.role is set for admin access
            g.role = 'admin'

            # Mock the view_all_assigned_assets method to raise an unexpected exception
            self.mock_asset_service.view_all_assigned_assets.side_effect = Exception("Unexpected error")

            response, status_code = self.asset_handler.assigned_all_assets()

            # Assert the response and status code
            self.assertEqual(status_code, 500)
            self.assertEqual(response["status_code"], ErrorCodes.DATABASE_OPERATION_ERROR)
            self.assertEqual(response["message"], "Error fetching assigned assets")

