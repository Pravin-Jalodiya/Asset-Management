from dataclasses import dataclass

from flask import request, jsonify
from werkzeug.routing import ValidationError

from AssetManagement.src.app.models.asset import Asset
from AssetManagement.src.app.models.asset_assigned import AssetAssigned
from AssetManagement.src.app.models.response import CustomResponse
from AssetManagement.src.app.services.asset_service import AssetService
from AssetManagement.src.app.utils.errors.error import (
    ExistsError,
    NotExistsError,
    NotAssignedError,
    AlreadyAssignedError
)
from AssetManagement.src.app.utils.logger.custom_logger import custom_logger
from AssetManagement.src.app.utils.logger.logger import Logger
from AssetManagement.src.app.utils.utils import Utils


@dataclass
class AssetHandler:
    asset_service: AssetService
    logger = Logger()

    @classmethod
    def create(cls, asset_service):
        return cls(asset_service)

    @custom_logger(logger)
    @Utils.admin
    def get_assets(self):
        """
        Handle request for all assets
        """
        try:
            results = self.asset_service.get_assets()
            results = [result.__dict__ for result in results] if results else []

            if results is not None:
                return jsonify(CustomResponse(
                    status_code=2101,  # Successfully fetched assets
                    message="Assets retrieved successfully",
                    data=results
                ).to_dict()), 200
            else:
                return jsonify(CustomResponse(
                    status_code=4101,  # No assets found
                    message="No assets found",
                    data=None
                ).to_dict()), 404
        except Exception as e:
            return jsonify(CustomResponse(
                status_code=5101,  # Error fetching assets
                message="Error fetching assets",
                data=None
            ).to_dict()), 500

    @custom_logger(logger)
    @Utils.admin
    def add_asset(self):
        """
        Handle adding a new asset
        - Validate asset details
        - Create and add asset
        """
        request_body = request.get_json()
        try:
            # Validate input fields
            name = request_body['name'].strip()
            if not name:
                raise ValidationError('Asset name cannot be empty')

            description = request_body['description'].strip()
            if not description:
                raise ValidationError('Description cannot be empty')

            serial_number = request_body['serial_number'].strip()
            if not serial_number:
                raise ValidationError('Serial number cannot be empty')

            # Create asset
            asset = Asset(
                name=name,
                description=description,
                serial_number=serial_number
            )

            # Add asset
            self.asset_service.add_asset(asset)

            return jsonify(CustomResponse(
                status_code=2102,  # Successfully added asset
                message="Asset added successfully",
                data=asset.__dict__
            ).to_dict()), 200
        except ExistsError as e:
            return jsonify(CustomResponse(
                status_code=4102,  # Asset already exists
                message=str(e),
                data=None
            ).to_dict()), 409
        except (ValidationError, ValueError) as e:
            return jsonify(CustomResponse(
                status_code=4103,  # Validation error
                message=str(e),
                data=None
            ).to_dict()), 400
        except Exception as e:
            return jsonify(CustomResponse(
                status_code=5102,  # Unexpected error during asset creation
                message="Unexpected error during asset creation",
                data=None
            ).to_dict()), 500

    @custom_logger(logger)
    @Utils.admin
    def delete_asset(self, asset_id: str):
        """
        Handle asset deletion
        """
        try:
            if not asset_id:
                raise ValidationError('Asset ID must be provided')

            deleted_asset = self.asset_service.delete_asset(asset_id)

            return jsonify(CustomResponse(
                status_code=2103,  # Successfully deleted asset
                message="Asset deleted successfully",
                data=deleted_asset.__dict__
            ).to_dict()), 200
        except NotExistsError as e:
            return jsonify(CustomResponse(
                status_code=4101,  # Asset not found
                message=str(e),
                data=None
            ).to_dict()), 404
        except (ValidationError, ValueError) as e:
            return jsonify(CustomResponse(
                status_code=4105,  # Validation error
                message=str(e),
                data=None
            ).to_dict()), 400
        except Exception as e:
            return jsonify(CustomResponse(
                status_code=5103,  # Error deleting asset
                message="Error deleting asset",
                data=None
            ).to_dict()), 500

    @custom_logger(logger)
    @Utils.admin
    def assign_asset(self):
        """
        Handle asset assignment to a user
        """
        request_body = request.get_json()
        try:
            user_id = request_body['user_id'].strip()
            asset_id = request_body['asset_id'].strip()

            if not user_id or not asset_id:
                raise ValidationError('User ID and Asset ID cannot be empty')

            assigned_asset = AssetAssigned(
                user_id=user_id,
                asset_id=asset_id,
            )

            self.asset_service.assign_asset(assigned_asset)

            return jsonify(CustomResponse(
                status_code=2104,  # Successfully assigned asset
                message="Asset assigned successfully",
                data=None
            ).to_dict()), 200
        except AlreadyAssignedError as e:
            return jsonify(CustomResponse(
                status_code=4106,  # Asset already assigned
                message=str(e),
                data=None
            ).to_dict()), 400
        except Exception as e:
            return jsonify(CustomResponse(
                status_code=5104,  # Error assigning asset
                message="Error assigning asset",
                data=None
            ).to_dict()), 500

    @custom_logger(logger)
    def unassign_asset(self):
        """
        Handle asset unassignment from a user
        """
        request_body = request.get_json()
        try:
            user_id = request_body['user_id'].strip()
            asset_id = request_body['asset_id'].strip()

            if not user_id or not asset_id:
                raise ValidationError('User ID and Asset ID cannot be empty')

            self.asset_service.unassign_asset(user_id, asset_id)

            return jsonify(CustomResponse(
                status_code=2105,  # Successfully unassigned asset
                message="Asset unassigned successfully",
                data=None
            ).to_dict()), 200
        except (NotExistsError, NotAssignedError) as e:
            return jsonify(CustomResponse(
                status_code=4107,  # Asset not assigned or not exists
                message=str(e),
                data=None
            ).to_dict()), 400
        except Exception as e:
            return jsonify(CustomResponse(
                status_code=5105,  # Error unassigning asset
                message="Error unassigning asset",
                data=None
            ).to_dict()), 500

    @custom_logger(logger)
    def assigned_assets(self, user_id: str):
        """
        Handle request for assets assigned to a user
        """
        try:
            if not user_id:
                return jsonify(CustomResponse(
                    status_code=4108,  # Missing user ID
                    message="User ID is required",
                    data=None
                ).to_dict()), 400

            results = self.asset_service.view_assigned_assets(user_id)

            if results is not None:
                return jsonify(CustomResponse(
                    status_code=2106,  # Successfully fetched assigned assets
                    message="Assigned assets retrieved successfully",
                    data=results
                ).to_dict()), 200
            else:
                return jsonify(CustomResponse(
                    status_code=4109,  # No assigned assets found
                    message="No assigned assets found",
                    data=None
                ).to_dict()), 404
        except Exception as e:
            return jsonify(CustomResponse(
                status_code=5106,  # Error fetching assigned assets
                message="Error fetching assigned assets",
                data=None
            ).to_dict()), 500

    @custom_logger(logger)
    @Utils.admin
    def assigned_all_assets(self):
        """
        Handle request for assets assigned to all users
        """
        try:
            results = self.asset_service.view_all_assigned_assets()

            if results is not None:
                return jsonify(CustomResponse(
                    status_code=2107,  # Successfully fetched all assigned assets
                    message="All assigned assets retrieved successfully",
                    data=results
                ).to_dict()), 200
            else:
                return jsonify(CustomResponse(
                    status_code=4110,  # No assigned assets found
                    message="No assigned assets found",
                    data=None
                ).to_dict()), 404
        except Exception as e:
            return jsonify(CustomResponse(
                status_code=5107,  # Error fetching all assigned assets
                message="Error fetching assigned assets",
                data=None
            ).to_dict()), 500
