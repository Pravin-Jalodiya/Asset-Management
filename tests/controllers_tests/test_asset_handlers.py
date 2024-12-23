import pytest
from unittest.mock import Mock
from fastapi import Request
from src.app.controllers.asset.handlers import AssetHandler
from src.app.models.asset import Asset
from src.app.models.request_objects import AssetRequest, AssignAssetRequest, UnassignAssetRequest
from src.app.utils.errors.error import NotExistsError, ExistsError, NotAssignedError, AlreadyAssignedError
from src.app.config.custom_error_codes import ErrorCodes
import uuid
from src.app.utils.validators.validators import Validators
import json


@pytest.fixture
def mock_request():
    """Mock FastAPI request fixture with admin role"""
    mock_scope = {
        "type": "http",
        "headers": [],
        "method": "GET",
        "path": "/",
        "query_string": b"",
        "client": ("127.0.0.1", 8000),
    }

    async def mock_receive():
        return {"type": "http.request", "body": b""}

    mock_request = Request(mock_scope, receive=mock_receive)
    mock_request.state.user = {"role": "admin", "user_id": "test-user"}
    return mock_request


@pytest.fixture
def mock_asset_service():
    """Mock asset service fixture"""
    return Mock()


@pytest.fixture
def asset_handler(mock_asset_service):
    """Asset handler fixture with mocked service"""
    return AssetHandler.create(mock_asset_service)


@pytest.fixture
def sample_asset():
    """Sample asset fixture"""
    asset = Asset(
        name="Test Asset",
        description="Test Description"
    )
    asset.id = "550e8400-e29b-41d4-a716-446655440000"
    return asset


@pytest.fixture
def sample_assets():
    """Sample list of assets fixture"""
    first_asset = Asset(
        name="First Asset",
        description="First Description"
    )
    first_asset.id = "550e8400-e29b-41d4-a716-446655440000"

    second_asset = Asset(
        name="Second Asset",
        description="Second Description"
    )
    second_asset.id = "650e8400-e29b-41d4-a716-446655440000"

    return [first_asset, second_asset]


@pytest.fixture
def valid_uuid():
    """Valid UUID fixture"""
    return str(uuid.uuid4())


class TestAssetHandler:
    """Test suite for AssetHandler"""

    @pytest.mark.asyncio
    async def test_get_assets_success(self, asset_handler, mock_request, sample_assets):
        # Arrange
        asset_handler.asset_service.get_assets.return_value = sample_assets

        # Act
        response = await asset_handler.get_assets(mock_request)

        # Assert
        assert response["status_code"] == 200
        assert response["message"] == "Assets fetched successfully"
        assert len(response["data"]) == 2
        assert response["data"][0]["name"] == "First Asset"
        assert response["data"][1]["name"] == "Second Asset"

    @pytest.mark.asyncio
    async def test_get_assets_database_error(self, asset_handler, mock_request):
        # Arrange
        asset_handler.asset_service.get_assets.side_effect = Exception("Database error")

        # Act
        response = await asset_handler.get_assets(mock_request)

        # Assert
        response_data = json.loads(response.body.decode()) if hasattr(response, 'body') else response
        assert response_data["status_code"] == ErrorCodes.DATABASE_OPERATION_ERROR.value
        assert response_data["message"] == "Error fetching assets"

    @pytest.mark.asyncio
    async def test_add_asset_success(self, asset_handler, mock_request, sample_asset):
        # Arrange
        asset_data = AssetRequest(
            name="Test Asset",
            description="Test Description"
        )
        asset_handler.asset_service.add_asset.return_value = sample_asset

        # Act
        response = await asset_handler.add_asset(mock_request, asset_data)

        # Assert
        assert response["status_code"] == 200
        assert response["message"] == "Asset added successfully"
        assert response["data"]["name"] == "Test Asset"

    @pytest.mark.asyncio
    async def test_add_asset_exists_error(self, asset_handler, mock_request):
        # Arrange
        asset_data = AssetRequest(
            name="Test Asset",
            description="Test Description"
        )
        asset_handler.asset_service.add_asset.side_effect = ExistsError("Asset already exists")

        # Act
        response = await asset_handler.add_asset(mock_request, asset_data)

        # Assert
        assert response["status_code"] == ErrorCodes.DUPLICATE_RECORD_ERROR.value
        assert response["message"] == "Asset already exists"

    @pytest.mark.asyncio
    async def test_add_asset_database_error(self, asset_handler, mock_request):
        # Arrange
        asset_data = AssetRequest(
            name="Test Asset",
            description="Test Description"
        )
        asset_handler.asset_service.add_asset.side_effect = Exception("Database error")

        # Act
        response = await asset_handler.add_asset(mock_request, asset_data)

        # Assert
        response_data = json.loads(response.body.decode())
        assert response.status_code == 500
        assert response_data["status_code"] == ErrorCodes.DATABASE_OPERATION_ERROR.value
        assert response_data["message"] == "Error adding asset"

    @pytest.mark.asyncio
    async def test_delete_asset_success(self, asset_handler, mock_request):
        # Arrange
        asset_id = "550e8400-e29b-41d4-a716-446655440000"

        # Act
        response = await asset_handler.delete_asset(mock_request, asset_id)

        # Assert
        assert response["status_code"] == 200
        assert response["message"] == "Asset deleted successfully"
        asset_handler.asset_service.delete_asset.assert_called_once_with(asset_id)

    @pytest.mark.asyncio
    async def test_delete_asset_not_found(self, asset_handler, mock_request):
        # Arrange
        asset_id = "550e8400-e29b-41d4-a716-446655440000"
        asset_handler.asset_service.delete_asset.side_effect = NotExistsError("Asset not found")

        # Act
        response = await asset_handler.delete_asset(mock_request, asset_id)

        # Assert
        assert response["status_code"] == ErrorCodes.RECORD_NOT_FOUND_ERROR.value
        assert response["message"] == "Asset not found"

    @pytest.mark.asyncio
    async def test_delete_asset_database_error(self, asset_handler, mock_request):
        # Arrange
        asset_id = "550e8400-e29b-41d4-a716-446655440000"
        asset_handler.asset_service.delete_asset.side_effect = Exception("Database error")

        # Act
        response = await asset_handler.delete_asset(mock_request, asset_id)

        # Assert
        response_data = json.loads(response.body.decode())
        assert response.status_code == 500
        assert response_data["status_code"] == ErrorCodes.DATABASE_OPERATION_ERROR.value
        assert response_data["message"] == "Error deleting asset"

    @pytest.mark.asyncio
    async def test_assign_asset_success(self, asset_handler, mock_request, valid_uuid):
        # Arrange
        assign_data = AssignAssetRequest(
            user_id=valid_uuid,
            asset_id=valid_uuid
        )

        # Act
        response = await asset_handler.assign_asset(mock_request, assign_data)

        # Assert
        assert response["status_code"] == 200
        assert response["message"] == "Asset assigned successfully"

    @pytest.mark.asyncio
    async def test_assign_asset_already_assigned(self, asset_handler, mock_request, valid_uuid):
        # Arrange
        assign_data = AssignAssetRequest(
            user_id=valid_uuid,
            asset_id=valid_uuid
        )
        asset_handler.asset_service.assign_asset.side_effect = AlreadyAssignedError("Asset already assigned")

        # Act
        response = await asset_handler.assign_asset(mock_request, assign_data)

        # Assert
        assert response["status_code"] == ErrorCodes.ASSET_ALREADY_ASSIGNED_ERROR.value
        assert response["message"] == "Asset already assigned"

    @pytest.mark.asyncio
    async def test_assign_asset_database_error(self, asset_handler, mock_request, valid_uuid):
        # Arrange
        assign_data = AssignAssetRequest(
            user_id=valid_uuid,
            asset_id=valid_uuid
        )
        asset_handler.asset_service.assign_asset.side_effect = Exception("Database error")

        # Act
        response = await asset_handler.assign_asset(mock_request, assign_data)

        # Assert
        response_data = json.loads(response.body.decode())
        assert response.status_code == 500
        assert response_data["status_code"] == ErrorCodes.DATABASE_OPERATION_ERROR.value
        assert response_data["message"] == "Error assigning asset"

    @pytest.mark.asyncio
    async def test_unassign_asset_success(self, asset_handler, valid_uuid):
        # Arrange
        unassign_data = UnassignAssetRequest(
            user_id=valid_uuid,
            asset_id=valid_uuid
        )

        # Act
        response = await asset_handler.unassign_asset(unassign_data)

        # Assert
        assert response["status_code"] == 200
        assert response["message"] == "Asset unassigned successfully"

    @pytest.mark.asyncio
    async def test_unassign_asset_not_assigned(self, asset_handler, valid_uuid):
        # Arrange
        unassign_data = UnassignAssetRequest(
            user_id=valid_uuid,
            asset_id=valid_uuid
        )
        asset_handler.asset_service.unassign_asset.side_effect = NotAssignedError("Asset not assigned")

        # Act
        response = await asset_handler.unassign_asset(unassign_data)

        # Assert
        assert response["status_code"] == ErrorCodes.ASSET_NOT_ASSIGNED_ERROR.value
        assert response["message"] == "Asset not assigned"

    @pytest.mark.asyncio
    async def test_unassign_asset_database_error(self, asset_handler, valid_uuid):
        # Arrange
        unassign_data = UnassignAssetRequest(
            user_id=valid_uuid,
            asset_id=valid_uuid
        )
        asset_handler.asset_service.unassign_asset.side_effect = Exception("Database error")

        # Act
        response = await asset_handler.unassign_asset(unassign_data)

        # Assert
        response_data = json.loads(response.body.decode())
        assert response.status_code == 500
        assert response_data["status_code"] == ErrorCodes.DATABASE_OPERATION_ERROR.value
        assert response_data["message"] == "Error unassigning asset"

    @pytest.mark.asyncio
    async def test_assigned_assets_success(self, asset_handler, sample_assets):
        # Arrange
        user_id = "test-user"
        asset_handler.asset_service.view_assigned_assets.return_value = sample_assets

        # Act
        response = await asset_handler.assigned_assets(user_id)

        # Assert
        assert response["status_code"] == 200
        assert response["message"] == "User assets fetched successfully"
        assert len(response["data"]) == 2

    @pytest.mark.asyncio
    async def test_assigned_assets_database_error(self, asset_handler):
        # Arrange
        user_id = "test-user"
        asset_handler.asset_service.view_assigned_assets.side_effect = Exception("Database error")

        # Act
        response = await asset_handler.assigned_assets(user_id)

        # Assert
        response_data = json.loads(response.body.decode())
        assert response.status_code == 500
        assert response_data["status_code"] == ErrorCodes.DATABASE_OPERATION_ERROR.value
        assert response_data["message"] == "Error fetching user assets"

    @pytest.mark.asyncio
    async def test_assigned_all_assets_success(self, asset_handler, mock_request, sample_assets):
        # Arrange
        asset_handler.asset_service.view_all_assigned_assets.return_value = sample_assets

        # Act
        response = await asset_handler.assigned_all_assets(mock_request)

        # Assert
        assert response["status_code"] == 200
        assert response["message"] == "All assigned assets fetched successfully"
        assert len(response["data"]) == 2

    @pytest.mark.asyncio
    async def test_assigned_all_assets_database_error(self, asset_handler, mock_request):
        # Arrange
        asset_handler.asset_service.view_all_assigned_assets.side_effect = Exception("Database error")

        # Act
        response = await asset_handler.assigned_all_assets(mock_request)

        # Assert
        response_data = json.loads(response.body.decode())
        assert response.status_code == 500
        assert response_data["status_code"] == ErrorCodes.DATABASE_OPERATION_ERROR.value
        assert response_data["message"] == "Error fetching assigned assets"
