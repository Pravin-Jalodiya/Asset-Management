from dataclasses import dataclass
from fastapi import Request
from src.app.models.asset import Asset
from src.app.models.asset_assigned import AssetAssigned
from src.app.models.request_objects import AssetRequest, AssignAssetRequest, UnassignAssetRequest
from src.app.services.asset_service import AssetService
from src.app.utils.errors.error import NotExistsError, ExistsError, NotAssignedError, AlreadyAssignedError
from src.app.utils.logger.custom_logger import custom_logger
from src.app.utils.logger.logger import Logger
from src.app.models.response import CustomResponse
from src.app.utils.utils import Utils
from src.app.config.custom_error_codes import ErrorCodes

@dataclass
class AssetHandler:
    asset_service: AssetService
    logger = Logger()

    @classmethod
    def create(cls, asset_service: AssetService):
        return cls(asset_service)

    @custom_logger(logger)
    @Utils.admin
    def get_assets(self, request: Request):
        try:
            assets = self.asset_service.get_assets()
            return CustomResponse(
                status_code=200,
                message="Assets fetched successfully",
                data=[asset.__dict__ for asset in assets] if assets else []
            ).object_to_dict()

        except Exception:
            return CustomResponse(
                status_code=ErrorCodes.DATABASE_OPERATION_ERROR,
                message="Error fetching assets",
                http_status_code=500
            ).to_response()

    @custom_logger(logger)
    @Utils.admin
    def add_asset(self, request: Request, asset_data: AssetRequest):
        try:
            asset = Asset(
                name=asset_data.name,
                description=asset_data.description
            )
            self.asset_service.add_asset(asset)

            return CustomResponse(
                status_code=200,
                message="Asset added successfully",
                data=asset.__dict__
            ).object_to_dict()

        except ExistsError as e:
            return CustomResponse(
                status_code=ErrorCodes.DUPLICATE_RECORD_ERROR,
                message=str(e)
            ).object_to_dict()

        except AlreadyAssignedError as e:
            return CustomResponse(
                status_code=ErrorCodes.ASSET_ALREADY_ASSIGNED_ERROR,
                message=str(e)
            ).object_to_dict()

        except Exception:
            return CustomResponse(
                status_code=ErrorCodes.DATABASE_OPERATION_ERROR,
                message="Error adding asset",
                http_status_code=500
            ).to_response()

    @custom_logger(logger)
    @Utils.admin
    def delete_asset(self, request: Request, asset_id: str):
        try:
            self.asset_service.delete_asset(asset_id)
            return CustomResponse(
                status_code=200,
                message="Asset deleted successfully"
            ).object_to_dict()

        except NotExistsError as e:
            return CustomResponse(
                status_code=ErrorCodes.RECORD_NOT_FOUND_ERROR,
                message=str(e)
            ).object_to_dict()

        except Exception:
            return CustomResponse(
                status_code=ErrorCodes.DATABASE_OPERATION_ERROR,
                message="Error deleting asset",
                http_status_code=500
            ).to_response()

    @custom_logger(logger)
    @Utils.admin
    def assign_asset(self, request: Request, assign_data: AssignAssetRequest):
        try:

            asset_assigned = AssetAssigned(
                user_id=assign_data.user_id,
                asset_id=assign_data.asset_id
            )

            self.asset_service.assign_asset(asset_assigned)

            return CustomResponse(
                status_code=200,
                message="Asset assigned successfully"
            ).object_to_dict()

        except NotExistsError as e:
            return CustomResponse(
                status_code=ErrorCodes.RECORD_NOT_FOUND_ERROR,
                message=str(e)
            ).object_to_dict()

        except AlreadyAssignedError as e:
            return CustomResponse(
                status_code=ErrorCodes.ASSET_ALREADY_ASSIGNED_ERROR,
                message=str(e)
            ).object_to_dict()

        except Exception as e:
            return CustomResponse(
                status_code=ErrorCodes.DATABASE_OPERATION_ERROR,
                message="Error assigning asset",
                http_status_code=500
            ).to_response()

    @custom_logger(logger)
    def unassign_asset(self, unassign_data: UnassignAssetRequest):
        try:
            self.asset_service.unassign_asset(
                str(unassign_data.user_id),
                str(unassign_data.asset_id)
            )

            return CustomResponse(
                status_code=200,
                message="Asset unassigned successfully"
            ).object_to_dict()

        except NotAssignedError as e:
            return CustomResponse(
                status_code=ErrorCodes.ASSET_NOT_ASSIGNED_ERROR,
                message=str(e)
            ).object_to_dict()

        except NotExistsError as e:
            return CustomResponse(
                status_code=ErrorCodes.ASSET_NOT_FOUND_ERROR,
                message=str(e)
            ).object_to_dict()

        except Exception as e:
            return CustomResponse(
                status_code=ErrorCodes.DATABASE_OPERATION_ERROR,
                message="Error unassigning asset",
                http_status_code=500
            ).to_response()

    @custom_logger(logger)
    def assigned_assets(self, user_id: str):
        try:
            assets = self.asset_service.view_assigned_assets(user_id)
            return CustomResponse(
                status_code=200,
                message="User assets fetched successfully",
                data=assets if assets else []
            ).object_to_dict()

        except NotExistsError as e:
            return CustomResponse(
                status_code=ErrorCodes.RECORD_NOT_FOUND_ERROR,
                message=str(e)
            ).object_to_dict()

        except Exception as e:
            return CustomResponse(
                status_code=ErrorCodes.DATABASE_OPERATION_ERROR,
                message="Error fetching user assets",
                http_status_code=500
            ).to_response()

    @custom_logger(logger)
    @Utils.admin
    def assigned_all_assets(self, request: Request):
        try:
            assets = self.asset_service.view_all_assigned_assets()
            return CustomResponse(
                status_code=200,
                message="All assigned assets fetched successfully",
                data=[asset for asset in assets] if assets else []
            ).object_to_dict()

        except Exception:
            return CustomResponse(
                status_code=ErrorCodes.DATABASE_OPERATION_ERROR,
                message="Error fetching assigned assets",
                http_status_code=500
            ).to_response()
