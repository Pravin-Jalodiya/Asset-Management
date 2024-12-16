from typing import List

from src.app.config.types import AssetStatus
from src.app.models.asset import Asset
from src.app.models.asset_assigned import AssetAssigned
from src.app.repositories.asset_repository import AssetRepository
from src.app.services.user_service import UserService
from src.app.utils.errors.error import (
    ExistsError,
    NotExistsError,
    NotAssignedError,
    AlreadyAssignedError
)


class AssetService:
    def __init__(self, asset_repository: AssetRepository, user_service: UserService):
        self.user_service = user_service
        self.asset_repository = asset_repository

    def get_assets(self):
        """Gets all assets"""
        return self.asset_repository.fetch_all_assets()

    def add_asset(self, asset: Asset):
        """Add a new asset"""
        # Check if the asset is already present
        result = self.asset_repository.fetch_asset_by_id(asset.serial_number)
        if result is None:
            self.asset_repository.add_asset(asset)
        else:
            raise ExistsError("Asset already exist")

    def delete_asset(self, asset_id: str):
        """Delete an existing asset"""
        # Check if the asset is even present or not
        asset = self.asset_repository.fetch_asset_by_id(asset_id)
        if asset is None:
            raise NotExistsError("Asset does not exist")
        else:
            self.asset_repository.delete_asset(asset_id)
            return asset

    def assign_asset(self, asset_assigned: AssetAssigned):
        """Assign an asset to a user"""
        # Check if the asset exists
        result = self.asset_repository.fetch_asset_by_id(asset_assigned.asset_id)
        if result is None:
            raise NotExistsError("Asset does not exist")

        # Check if the user exists
        result = self.user_service.get_user_by_id(asset_assigned.user_id)
        if result is None:
            raise NotExistsError("User does not exist")

        # Check if asset is assigned to any user
        if self.asset_repository.check_asset_availability(asset_assigned.asset_id):
            self.asset_repository.assign_asset(asset_assigned)
            self.asset_repository.update_asset_status(asset_assigned.asset_id, AssetStatus.ASSIGNED.value)
        else:
            if self.asset_repository.is_asset_assigned(asset_assigned.user_id, asset_assigned.asset_id):
                raise AlreadyAssignedError("Asset already assigned to the user")
            else:
                raise AlreadyAssignedError("Asset already assigned to other user")

    def unassign_asset(self, user_id: str, asset_id: str):
        """Unassign an asset to a user"""
        # Check if the asset exists
        result = self.asset_repository.fetch_asset_by_id(asset_id)
        if result is None:
            raise NotExistsError("Asset does not exist")

        # Check if the user exists
        result = self.user_service.get_user_by_id(user_id)
        if result is None:
            raise NotExistsError("User does not exist")

        if self.asset_repository.is_asset_assigned(user_id, asset_id):
            self.asset_repository.unassign_asset(user_id, asset_id)
            self.asset_repository.update_asset_status(asset_id, AssetStatus.AVAILABLE.value)
        else:
            raise NotAssignedError("Asset is not assigned to the user")

    def view_assigned_assets(self, user_id: str) -> dict:
        """
        Retrieve all assets assigned to a user
        """
        result = self.user_service.get_user_by_id(user_id)
        if result is None:
            raise NotExistsError("User does not exist")

        return self.asset_repository.view_assigned_assets(user_id)

    def view_all_assigned_assets(self) -> List[dict]:
        return self.asset_repository.view_all_assigned_assets()

    def get_asset_by_id(self, asset_id: str):
        return self.asset_repository.fetch_asset_by_id(asset_id)

    def is_asset_assigned(self, user_id: str, asset_id: str):
        return self.asset_repository.is_asset_assigned(user_id, asset_id)
