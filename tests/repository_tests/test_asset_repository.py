import unittest
from unittest.mock import MagicMock, patch
from src.app.repositories.asset_repository import AssetRepository
from src.app.models.asset import Asset
from src.app.models.asset_assigned import AssetAssigned
from src.app.utils.errors.error import DatabaseError, AssetAlreadyAssignedError
from src.app.config.types import AssetStatus


class TestAssetRepository(unittest.TestCase):
    @patch("src.app.utils.db.db.DB")
    @patch("src.app.utils.db.query_builder.GenericQueryBuilder")
    def setUp(self, mock_query_builder, mock_db):
        # Initialize mocked DB and QueryBuilder
        self.mock_db = mock_db
        self.mock_query_builder = mock_query_builder

        # Mock DB connection and cursor
        self.mock_conn = MagicMock()
        self.mock_cursor = MagicMock()
        self.mock_db.get_connection.return_value = self.mock_conn
        self.mock_conn.cursor.return_value = self.mock_cursor

        # Initialize AssetRepository with mocked DB
        self.asset_repository = AssetRepository(self.mock_db)

    def test_add_asset_success(self):
        # Arrange
        asset = Asset(
            name="Laptop",
            description="Dell XPS"
        )

        # We'll capture the actual serial number generated
        asset_data = {
            "serial_number": asset.serial_number,
            "name": "Laptop",
            "description": "Dell XPS",
            "status": AssetStatus.AVAILABLE.value
        }

        # Mock the insert method to return query and values
        query = "INSERT INTO assets (serial_number, name, description, status) VALUES (?, ?, ?, ?)"
        values = list(asset_data.values())
        self.mock_query_builder.insert.return_value = (query, values)

        # Act
        self.asset_repository.add_asset(asset)

        # Assert
        self.mock_cursor.execute.assert_called_once_with(query, values)

    def test_add_asset_raises_database_error(self):
        # Arrange
        asset = Asset(
            serial_number="SN001",
            name="Laptop",
            description="Dell XPS",
            status=AssetStatus.AVAILABLE.value
        )
        self.mock_conn.cursor.side_effect = Exception("Database connection error")

        # Act & Assert
        with self.assertRaises(DatabaseError):
            self.asset_repository.add_asset(asset)

    def test_fetch_all_assets_success(self):
        # Arrange
        mock_results = [
            ("SN001", "Laptop", "Dell XPS", AssetStatus.AVAILABLE.value),
            ("SN002", "Desktop", "HP Workstation", AssetStatus.ASSIGNED.value)
        ]
        self.mock_cursor.fetchall.return_value = mock_results
        query = "SELECT serial_number, name, description, status FROM assets"
        values = ()
        self.mock_query_builder.select.return_value = (query, values)

        # Act
        assets = self.asset_repository.fetch_all_assets()

        # Assert
        self.assertEqual(len(assets), 2)
        self.assertEqual(assets[0].serial_number, "SN001")
        self.assertEqual(assets[1].name, "Desktop")

    def test_fetch_all_assets_raises_database_error(self):
        self.mock_conn.cursor.side_effect = Exception("Database connection error")

        # Act & Assert
        with self.assertRaises(DatabaseError):
            self.asset_repository.fetch_all_assets()


    def test_fetch_asset_by_id_success(self):
        # Arrange
        asset_id = "SN001"
        mock_result = ("SN001", "Laptop", "Dell XPS", AssetStatus.AVAILABLE.value)
        self.mock_cursor.fetchone.return_value = mock_result

        # Act
        asset = self.asset_repository.fetch_asset_by_id(asset_id)

        # Assert
        self.assertIsNotNone(asset)
        self.assertEqual(asset.serial_number, "SN001")
        self.assertEqual(asset.name, "Laptop")

    def test_fetch_asset_by_id_not_found(self):
        # Arrange
        asset_id = "SN999"
        self.mock_cursor.fetchone.return_value = None

        # Act
        asset = self.asset_repository.fetch_asset_by_id(asset_id)

        # Assert
        self.assertIsNone(asset)

    def test_fetch_asset_by_id_raises_database_error(self):
        test_id = "test_id"
        self.mock_conn.cursor.side_effect = Exception("Database connection error")

        # Act & Assert
        with self.assertRaises(DatabaseError):
            self.asset_repository.fetch_asset_by_id(test_id)

    def test_assign_asset_success(self):
        # Arrange
        asset_assigned = AssetAssigned(
            user_id="U001",
            asset_id="SN001",
        )
        query = "INSERT INTO assets_assigned ..."
        values = ("U001", "SN001", asset_assigned.asset_assigned_id, asset_assigned.assigned_date)
        self.mock_query_builder.insert.return_value = (query, values)

        # Act
        self.asset_repository.assign_asset(asset_assigned)

        # Assert
        self.mock_cursor.execute.assert_called_once()

    def test_assign_asset_raises_database_error(self):
        asset_assigned = AssetAssigned(
            user_id="U001",
            asset_id="SN001",
        )
        self.mock_conn.cursor.side_effect = Exception("Database connection error")

        # Act & Assert
        with self.assertRaises(DatabaseError):
            self.asset_repository.assign_asset(asset_assigned)

    def test_unassign_asset_success(self):
        # Arrange
        user_id = "U001"
        asset_id = "SN001"
        query = "DELETE FROM assets_assigned ..."
        values = (user_id, asset_id)
        self.mock_query_builder.delete.return_value = (query, values)

        # Act
        self.asset_repository.unassign_asset(user_id, asset_id)

        # Assert
        self.mock_cursor.execute.assert_called_once()

    def test_unassign_asset_raises_database_error(self):
        asset_assigned = AssetAssigned(
            user_id="U001",
            asset_id="SN001",
        )
        self.mock_conn.cursor.side_effect = Exception("Database connection error")

        # Act & Assert
        with self.assertRaises(DatabaseError):
            self.asset_repository.unassign_asset(asset_assigned.user_id, asset_assigned.asset_id)

    def test_update_asset_status_success(self):
        # Arrange
        asset_id = "SN001"
        new_status = AssetStatus.ASSIGNED.value
        query = "UPDATE assets SET ..."
        values = (new_status, asset_id)
        self.mock_query_builder.update.return_value = (query, values)

        # Act
        self.asset_repository.update_asset_status(asset_id, new_status)

        # Assert
        self.mock_cursor.execute.assert_called_once()

    def test_update_asset_status_raises_database_error(self):
        asset_id = "SN001"
        new_status = AssetStatus.ASSIGNED.value

        self.mock_conn.cursor.side_effect = Exception("Database connection error")

        # Act & Assert
        with self.assertRaises(DatabaseError):
            self.asset_repository.update_asset_status(asset_id, new_status)

    def test_check_asset_availability_available(self):
        # Arrange
        asset_id = "SN001"
        self.mock_cursor.fetchone.return_value = (AssetStatus.AVAILABLE.value,)

        # Act
        is_available = self.asset_repository.check_asset_availability(asset_id)

        # Assert
        self.assertTrue(is_available)

    def test_check_asset_availability_available_raises_database_error(self):
        # Arrange
        asset_id = "SN001"

        # Act
        self.mock_conn.cursor.side_effect = Exception("Database connection error")

        # Assert
        with self.assertRaises(AssetAlreadyAssignedError):
            self.asset_repository.check_asset_availability(asset_id)


    def test_check_asset_availability_not_available(self):
        # Arrange
        asset_id = "SN001"
        self.mock_cursor.fetchone.return_value = (AssetStatus.ASSIGNED.value,)

        # Act
        is_available = self.asset_repository.check_asset_availability(asset_id)

        # Assert
        self.assertFalse(is_available)

    def test_delete_asset_success(self):
        # Arrange
        asset_id = "SN001"
        query = "DELETE FROM assets ..."
        values = (asset_id,)
        self.mock_query_builder.delete.return_value = (query, values)

        # Act
        self.asset_repository.delete_asset(asset_id)

        # Assert
        self.mock_cursor.execute.assert_called_once()

    def test_delete_asset_success_raises_database_error(self):
        # Arrange
        asset_id = "SN001"
        query = "DELETE FROM assets ..."
        values = (asset_id,)
        self.mock_query_builder.delete.return_value = (query, values)

        # Act
        self.mock_conn.cursor.side_effect = Exception("Database connection error")

        # Assert
        with self.assertRaises(DatabaseError):
            self.asset_repository.delete_asset(asset_id)

    def test_is_asset_assigned_true(self):
        # Arrange
        user_id = "U001"
        asset_id = "SN001"
        self.mock_cursor.fetchone.return_value = (user_id, asset_id)

        # Act
        is_assigned = self.asset_repository.is_asset_assigned(user_id, asset_id)

        # Assert
        self.assertTrue(is_assigned)

    def test_is_asset_assigned_false(self):
        # Arrange
        user_id = "U001"
        asset_id = "SN001"
        self.mock_cursor.fetchone.return_value = None

        # Act
        is_assigned = self.asset_repository.is_asset_assigned(user_id, asset_id)

        # Assert
        self.assertFalse(is_assigned)

    def test_is_asset_assigned_raises_database_error(self):
        # Arrange
        user_id = "U001"
        asset_id = "SN001"
        self.mock_cursor.fetchone.return_value = None

        # Act
        self.mock_conn.cursor.side_effect = Exception("Database error")

        # Assert
        with self.assertRaises(DatabaseError):
            self.asset_repository.is_asset_assigned(user_id, asset_id)


    def test_view_assigned_assets_success(self):
        # Arrange
        user_id = "U001"
        mock_results = [
            ("SN001", "Laptop", "Dell XPS", AssetStatus.ASSIGNED.value),
            ("SN002", "Desktop", "HP Workstation", AssetStatus.ASSIGNED.value)
        ]
        self.mock_cursor.fetchall.return_value = mock_results

        # Act
        result = self.asset_repository.view_assigned_assets(user_id)

        # Assert
        self.assertEqual(result["user_id"], user_id)
        self.assertEqual(len(result["assets"]), 2)
        self.assertEqual(result["assets"][0]["serial_number"], "SN001")

    def test_view_assigned_assets_no_assets(self):
        # Arrange
        user_id = "U001"
        self.mock_cursor.fetchall.return_value = []

        # Act
        result = self.asset_repository.view_assigned_assets(user_id)

        # Assert
        self.assertEqual(result["user_id"], user_id)
        self.assertEqual(len(result["assets"]), 0)

    def test_view_assigned_assets_no_assets_raises_database_error(self):
        # Arrange
        user_id = "U001"
        self.mock_cursor.fetchall.return_value = []

        # Act
        self.mock_conn.cursor.side_effect = Exception("Database error")

        # Assert
        with self.assertRaises(DatabaseError):
            self.asset_repository.view_assigned_assets(user_id)

    def test_view_all_assigned_assets_success(self):
        # Arrange
        mock_results = [
            ("U001", "SN001,SN002"),
            ("U002", "SN003")
        ]
        self.mock_cursor.fetchall.return_value = mock_results

        # Act
        result = self.asset_repository.view_all_assigned_assets()

        # Assert
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["user_id"], "U001")
        self.assertEqual(result[0]["asset_ids"], ["SN001", "SN002"])
        self.assertEqual(result[1]["asset_ids"], ["SN003"])

    def test_view_all_assigned_assets_raises_database_error(self):
        # Arrange
        self.mock_cursor.fetchall.return_value = []

        # Act
        self.mock_conn.cursor.side_effect = Exception("Database error")

        # Assert
        with self.assertRaises(DatabaseError):
            self.asset_repository.view_all_assigned_assets()
