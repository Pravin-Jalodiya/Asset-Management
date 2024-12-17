import unittest
from unittest.mock import MagicMock
import uuid

from src.app.models.asset import Asset
from src.app.models.asset_assigned import AssetAssigned
from src.app.services.asset_service import AssetService
from src.app.config.types import AssetStatus
from src.app.utils.errors.error import (
    ExistsError,
    NotExistsError,
)


class TestAssetService(unittest.TestCase):
    def setUp(self):
        # Create mock dependencies
        self.mock_asset_repository = MagicMock()
        self.mock_user_service = MagicMock()

        # Initialize the service with mock dependencies
        self.asset_service = AssetService(
            asset_repository=self.mock_asset_repository,
            user_service=self.mock_user_service
        )

    def test_get_assets(self):
        """
        Test retrieving all assets
        """
        # Arrange
        expected_assets = [
            Asset(name="Laptop", description="Work laptop", serial_number="SN001"),
            Asset(name="Monitor", description="Dell monitor", serial_number="SN002")
        ]
        self.mock_asset_repository.fetch_all_assets.return_value = expected_assets

        # Act
        result = self.asset_service.get_assets()

        # Assert
        self.assertEqual(result, expected_assets)
        self.mock_asset_repository.fetch_all_assets.assert_called_once()

    def test_add_asset_successful(self):
        """
        Test adding a new asset successfully
        """
        # Arrange
        new_asset = Asset(
            name="New Laptop",
            description="Brand new laptop",
            serial_number="SN003"
        )
        # Simulate no existing asset with this serial number
        self.mock_asset_repository.fetch_asset_by_id.return_value = None

        # Act
        self.asset_service.add_asset(new_asset)

        # Assert
        self.mock_asset_repository.fetch_asset_by_id.assert_called_once_with(new_asset.serial_number)
        self.mock_asset_repository.add_asset.assert_called_once_with(new_asset)

    def test_add_asset_raises_exists_error(self):
        """
        Test adding an asset that already exists
        """
        # Arrange
        existing_asset = Asset(
            name="Existing Laptop",
            description="Already in inventory",
            serial_number="SN004"
        )
        # Simulate an existing asset with this serial number
        self.mock_asset_repository.fetch_asset_by_id.return_value = existing_asset

        # Act & Assert
        with self.assertRaises(ExistsError) as context:
            self.asset_service.add_asset(existing_asset)

        self.assertEqual(str(context.exception), "Asset already exist")
        self.mock_asset_repository.add_asset.assert_not_called()

    def test_delete_asset_successful(self):
        """
        Test deleting an existing asset
        """
        # Arrange
        asset_id = "SN005"
        existing_asset = Asset(
            name="Test Laptop",
            description="To be deleted",
            serial_number=asset_id
        )
        # Simulate finding the asset
        self.mock_asset_repository.fetch_asset_by_id.return_value = existing_asset

        # Act
        result = self.asset_service.delete_asset(asset_id)

        # Assert
        self.assertEqual(result, existing_asset)
        self.mock_asset_repository.fetch_asset_by_id.assert_called_once_with(asset_id)
        self.mock_asset_repository.delete_asset.assert_called_once_with(asset_id)

    def test_delete_asset_raises_not_exists_error(self):
        """
        Test deleting a non-existent asset
        """
        # Arrange
        asset_id = "NONEXISTENT"
        # Simulate no asset found
        self.mock_asset_repository.fetch_asset_by_id.return_value = None

        # Act & Assert
        with self.assertRaises(NotExistsError) as context:
            self.asset_service.delete_asset(asset_id)

        self.assertEqual(str(context.exception), "Asset does not exist")
        self.mock_asset_repository.delete_asset.assert_not_called()

    def test_assign_asset_successful(self):
        """
        Test assigning an asset to a user successfully
        """
        # Arrange
        asset_id = "SN006"
        user_id = str(uuid.uuid4())
        asset_assigned = AssetAssigned(
            asset_id=asset_id,
            user_id=user_id
        )

        # Simulate asset and user exist, asset is available
        self.mock_asset_repository.fetch_asset_by_id.return_value = Asset(
            name="Testable Asset",
            description="Ready to assign",
            serial_number=asset_id
        )
        self.mock_user_service.get_user_by_id.return_value = {"id": user_id}
        self.mock_asset_repository.check_asset_availability.return_value = True

        # Act
        self.asset_service.assign_asset(asset_assigned)

        # Assert
        self.mock_asset_repository.fetch_asset_by_id.assert_called_once_with(asset_id)
        self.mock_user_service.get_user_by_id.assert_called_once_with(user_id)
        self.mock_asset_repository.assign_asset.assert_called_once_with(asset_assigned)
        self.mock_asset_repository.update_asset_status.assert_called_once_with(
            asset_id,
            AssetStatus.ASSIGNED.value
        )

    def test_assign_asset_raises_asset_not_exists_error(self):
        """
        Test assigning a non-existent asset
        """
        # Arrange
        asset_id = "NONEXISTENT"
        user_id = str(uuid.uuid4())
        asset_assigned = AssetAssigned(
            asset_id=asset_id,
            user_id=user_id
        )

        # Simulate asset does not exist
        self.mock_asset_repository.fetch_asset_by_id.return_value = None

        # Act & Assert
        with self.assertRaises(NotExistsError) as context:
            self.asset_service.assign_asset(asset_assigned)

        self.assertEqual(str(context.exception), "Asset does not exist")
        self.mock_asset_repository.assign_asset.assert_not_called()

    def test_assign_asset_raises_user_not_exists_error(self):
        """
        Test assigning asset to a non-existent user
        """
        # Arrange
        asset_id = "SN007"
        user_id = "NONEXISTENT"
        asset_assigned = AssetAssigned(
            asset_id=asset_id,
            user_id=user_id
        )

        # Simulate asset exists but user does not
        self.mock_asset_repository.fetch_asset_by_id.return_value = Asset(
            name="Test Asset",
            description="Available asset",
            serial_number=asset_id
        )
        self.mock_user_service.get_user_by_id.return_value = None

        # Act & Assert
        with self.assertRaises(NotExistsError) as context:
            self.asset_service.assign_asset(asset_assigned)

        self.assertEqual(str(context.exception), "User does not exist")
        self.mock_asset_repository.assign_asset.assert_not_called()

    def test_unassign_asset_successful(self):
        """
        Test unassigning an asset from a user successfully
        """
        # Arrange
        asset_id = "SN008"
        user_id = str(uuid.uuid4())

        # Simulate asset and user exist, and asset is assigned to user
        self.mock_asset_repository.fetch_asset_by_id.return_value = Asset(
            name="Test Asset",
            description="Assigned asset",
            serial_number=asset_id
        )
        self.mock_user_service.get_user_by_id.return_value = {"id": user_id}
        self.mock_asset_repository.is_asset_assigned.return_value = True

        # Act
        self.asset_service.unassign_asset(user_id, asset_id)

        # Assert
        self.mock_asset_repository.fetch_asset_by_id.assert_called_once_with(asset_id)
        self.mock_user_service.get_user_by_id.assert_called_once_with(user_id)
        self.mock_asset_repository.unassign_asset.assert_called_once_with(user_id, asset_id)
        self.mock_asset_repository.update_asset_status.assert_called_once_with(
            asset_id,
            AssetStatus.AVAILABLE.value
        )

    def test_unassign_asset_raises_not_exists_errors(self):
        """
        Test unassigning asset raises errors for non-existent asset or user
        """
        # Arrange
        asset_id = "NONEXISTENT"
        user_id = str(uuid.uuid4())

        # Simulate asset does not exist
        self.mock_asset_repository.fetch_asset_by_id.return_value = None

        # Act & Assert
        with self.assertRaises(NotExistsError) as context:
            self.asset_service.unassign_asset(user_id, asset_id)

        self.assertEqual(str(context.exception), "Asset does not exist")

    def test_view_assigned_assets_successful(self):
        """
        Test viewing assets assigned to a user
        """
        # Arrange
        user_id = str(uuid.uuid4())
        expected_assets = [
            {"asset_id": "SN009", "name": "Laptop"},
            {"asset_id": "SN010", "name": "Monitor"}
        ]

        # Simulate user exists
        self.mock_user_service.get_user_by_id.return_value = {"id": user_id}
        self.mock_asset_repository.view_assigned_assets.return_value = expected_assets

        # Act
        result = self.asset_service.view_assigned_assets(user_id)

        # Assert
        self.assertEqual(result, expected_assets)
        self.mock_user_service.get_user_by_id.assert_called_once_with(user_id)
        self.mock_asset_repository.view_assigned_assets.assert_called_once_with(user_id)

    def test_view_assigned_assets_raises_user_not_exists_error(self):
        """
        Test viewing assets for a non-existent user
        """
        # Arrange
        user_id = "NONEXISTENT"

        # Simulate user does not exist
        self.mock_user_service.get_user_by_id.return_value = None

        # Act & Assert
        with self.assertRaises(NotExistsError) as context:
            self.asset_service.view_assigned_assets(user_id)

        self.assertEqual(str(context.exception), "User does not exist")

    def test_view_all_assigned_assets(self):
        """
        Test viewing all assigned assets
        """
        # Arrange
        expected_assets = [
            {"asset_id": "SN011", "user_id": str(uuid.uuid4())},
            {"asset_id": "SN012", "user_id": str(uuid.uuid4())}
        ]
        self.mock_asset_repository.view_all_assigned_assets.return_value = expected_assets

        # Act
        result = self.asset_service.view_all_assigned_assets()

        # Assert
        self.assertEqual(result, expected_assets)
        self.mock_asset_repository.view_all_assigned_assets.assert_called_once()

    def test_get_asset_by_id(self):
        """
        Test retrieving an asset by its ID
        """
        # Arrange
        asset_id = "SN013"
        expected_asset = Asset(
            name="Test Asset",
            description="Retrievable asset",
            serial_number=asset_id
        )
        self.mock_asset_repository.fetch_asset_by_id.return_value = expected_asset

        # Act
        result = self.asset_service.get_asset_by_id(asset_id)

        # Assert
        self.assertEqual(result, expected_asset)
        self.mock_asset_repository.fetch_asset_by_id.assert_called_once_with(asset_id)

    def test_is_asset_assigned(self):
        """
        Test checking if an asset is assigned to a user
        """
        # Arrange
        user_id = str(uuid.uuid4())
        asset_id = "SN014"
        self.mock_asset_repository.is_asset_assigned.return_value = True

        # Act
        result = self.asset_service.is_asset_assigned(user_id, asset_id)

        # Assert
        self.assertTrue(result)
        self.mock_asset_repository.is_asset_assigned.assert_called_once_with(user_id, asset_id)
