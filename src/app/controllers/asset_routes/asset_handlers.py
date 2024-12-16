from dataclasses import dataclass

from flask import request, jsonify
from werkzeug.routing import ValidationError

from src.app.models.asset import Asset
from src.app.models.asset_assigned import AssetAssigned
from src.app.models.request_objects import AssetRequest, AssignAssetRequest, UnassignAssetRequest
from src.app.models.response import CustomResponse
from src.app.services.asset_service import AssetService
from src.app.utils.errors.error import (
    ExistsError,
    NotExistsError,
    NotAssignedError,
    AlreadyAssignedError,
    DatabaseError
)
from src.app.utils.logger.custom_logger import custom_logger
from src.app.utils.logger.logger import Logger
from src.app.utils.utils import Utils
from src.app.utils.validators.validators import Validators

# Import new error codes
from src.app.config.custom_error_codes import (
    VALIDATION_ERROR,
    DUPLICATE_RECORD_ERROR,
    RECORD_NOT_FOUND_ERROR,
    ASSET_ALREADY_ASSIGNED_ERROR,
    ASSET_NOT_ASSIGNED_ERROR,
    DATABASE_OPERATION_ERROR
)

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
        try:
            results = self.asset_service.get_assets()
            results = [result.__dict__ for result in results] if results else []

            if results is not None:
                return CustomResponse(
                    status_code=200,
                    message="Assets retrieved successfully",
                    data=results
                ).to_dict(), 200

        except (DatabaseError, Exception) as e:
            return CustomResponse(
                status_code=DATABASE_OPERATION_ERROR,
                message="Error fetching assets",
                data=None
            ).to_dict(), 500

    @custom_logger(logger)
    @Utils.admin
    def add_asset(self):
        try:
            asset_data = AssetRequest(request.get_json())

            # Create asset
            asset = Asset(
                name=asset_data.name,
                description=asset_data.description
            )

            # Add asset
            self.asset_service.add_asset(asset)

            return CustomResponse(
                status_code=200,
                message="Asset added successfully",
                data=asset.__dict__
            ).to_dict(), 200

        except ExistsError as e:
            return CustomResponse(
                status_code=DUPLICATE_RECORD_ERROR,
                message=str(e),
                data=None
            ).to_dict(), 409

        except ValidationError as e:
            return CustomResponse(
                status_code=VALIDATION_ERROR,
                message=str(e),
                data=None
            ).to_dict(), 400

        except (DatabaseError, Exception) as e:
            return CustomResponse(
                status_code=DATABASE_OPERATION_ERROR,
                message="Unexpected error during asset creation",
                data=None
            ).to_dict(), 500

    @custom_logger(logger)
    @Utils.admin
    def delete_asset(self, asset_id: str):
        try:
            is_valid = Validators.is_valid_UUID(asset_id)
            if is_valid:
                deleted_asset = self.asset_service.delete_asset(asset_id)
                return CustomResponse(
                    status_code=200,
                    message="Asset deleted successfully",
                    data=deleted_asset.__dict__
                ).to_dict(), 200

            else:
                return CustomResponse(
                    status_code=VALIDATION_ERROR,
                    message="Invalid asset id",
                    data=None
                ).to_dict(), 400

        except NotExistsError as e:
            return CustomResponse(
                status_code=RECORD_NOT_FOUND_ERROR,
                message=str(e),
                data=None
            ).to_dict(), 404

        except ValidationError as e:
            return CustomResponse(
                status_code=VALIDATION_ERROR,
                message=str(e),
                data=None
            ).to_dict(), 400

        except (DatabaseError, Exception) as e:
            return CustomResponse(
                status_code=DATABASE_OPERATION_ERROR,
                message="Error deleting asset",
                data=None
            ).to_dict(), 500

    @custom_logger(logger)
    @Utils.admin
    def assign_asset(self):
        try:
            assign_asset_data = AssignAssetRequest(request.get_json())

            assigned_asset = AssetAssigned(
                user_id=assign_asset_data.user_id,
                asset_id=assign_asset_data.asset_id,
            )

            self.asset_service.assign_asset(assigned_asset)

            return CustomResponse(
                status_code=200,  # Kept as is for successful assignment
                message="Asset assigned successfully",
                data=None
            ).to_dict(), 200

        except ValidationError as e:
            return CustomResponse(
                status_code=VALIDATION_ERROR,
                message=str(e),
                data=None
            ).to_dict(), 400

        except AlreadyAssignedError as e:
            return CustomResponse(
                status_code=ASSET_ALREADY_ASSIGNED_ERROR,
                message=str(e),
                data=None
            ).to_dict(), 400

        except NotExistsError as e:
            return CustomResponse(
                status_code=RECORD_NOT_FOUND_ERROR,
                message=str(e),
                data=None
            ).to_dict(), 400

        except (DatabaseError, Exception) as e:
            return CustomResponse(
                status_code=DATABASE_OPERATION_ERROR,
                message="Error assigning asset",
                data=None
            ).to_dict(), 500

    @custom_logger(logger)
    def unassign_asset(self):
        try:
            unassign_asset_data = UnassignAssetRequest(request.get_json())

            self.asset_service.unassign_asset(unassign_asset_data.user_id, unassign_asset_data.asset_id)

            return CustomResponse(
                status_code=200,
                message="Asset unassigned successfully",
                data=None
            ).to_dict(), 200

        except NotExistsError as e:
            return CustomResponse(
                status_code=RECORD_NOT_FOUND_ERROR,
                message=str(e),
                data=None
            ).to_dict(), 400

        except ValidationError as e:
            return CustomResponse(
                status_code=VALIDATION_ERROR,
                message=str(e),
                data=None
            ).to_dict(), 400

        except NotAssignedError as e:
            return CustomResponse(
                status_code=ASSET_NOT_ASSIGNED_ERROR,
                message=str(e),
                data=None
            ).to_dict(), 400

        except (DatabaseError, Exception) as e:
            return CustomResponse(
                status_code=DATABASE_OPERATION_ERROR,
                message="Error unassigning asset",
                data=None
            ).to_dict(), 500

    @custom_logger(logger)
    def assigned_assets(self, user_id: str):
        try:
            is_valid = Validators.is_valid_UUID(user_id)
            if is_valid:
                results = self.asset_service.view_assigned_assets(user_id)

                if results is not None:
                    return CustomResponse(
                        status_code=200,
                        message="Assigned assets retrieved successfully",
                        data=results
                    ).to_dict(), 200

            else:
                return CustomResponse(
                    status_code=VALIDATION_ERROR,
                    message="Invalid user id",
                    data=None
                ).to_dict(), 200

        except NotExistsError as e:
            return CustomResponse(
                status_code=RECORD_NOT_FOUND_ERROR,
                message=str(e),
                data=None
            ).to_dict(), 400

        except ValidationError as e:
            return CustomResponse(
                status_code=VALIDATION_ERROR,
                message=str(e),
                data=None
            ).to_dict(), 400

        except (DatabaseError, Exception) as e:
            return CustomResponse(
                status_code=DATABASE_OPERATION_ERROR,
                message="Error fetching assigned assets",
                data=None
            ).to_dict(), 500

    @custom_logger(logger)
    @Utils.admin
    def assigned_all_assets(self):
        try:
            results = self.asset_service.view_all_assigned_assets()

            if results is not None:
                return CustomResponse(
                    status_code=200,
                    message="All assigned assets retrieved successfully",
                    data=results
                ).to_dict(), 200

        except (DatabaseError, Exception) as e:
            return CustomResponse(
                status_code=DATABASE_OPERATION_ERROR,
                message="Error fetching assigned assets",
                data=None
            ).to_dict(), 500