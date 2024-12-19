from dataclasses import dataclass
from src.app.models.asset import Asset
from src.app.models.request_objects import AssetRequest, AssignAssetRequest, UnassignAssetRequest
from src.app.services.asset_service import AssetService
from src.app.utils.errors.error import NotExistsError, ExistsError, NotAssignedError
from src.app.utils.logger.custom_logger import custom_logger
from src.app.utils.logger.logger import Logger
from src.app.utils.utils import Utils
from src.app.models.response import CustomResponse

@dataclass
class AssetHandler:
    asset_service: AssetService
    logger = Logger()

    @classmethod
    def create(cls, asset_service: AssetService):
        return cls(asset_service)

    @custom_logger(logger)
    async def get_assets(self):
        try:
            assets = await self.asset_service.get_assets()
            return CustomResponse(
                status_code=200,
                message="Assets fetched successfully",
                data=[asset.dict() for asset in assets] if assets else []
            )
        except Exception as e:
            return CustomResponse(
                status_code=500,
                message="Error fetching assets"
            )

    @custom_logger(logger)
    async def add_asset(self, asset_data: AssetRequest):
        try:
            asset = Asset(
                name=asset_data.name,
                description=asset_data.description
            )
            await self.asset_service.add_asset(asset)
            return CustomResponse(
                status_code=201,
                message="Asset added successfully",
                data=asset.__dict__
            )
        except ExistsError as e:
            return CustomResponse(
                status_code=409,
                message=str(e)
            )
        except Exception as e:
            return CustomResponse(
                status_code=500,
                message="Error adding asset"
            )

    @custom_logger(logger)
    async def delete_asset(self, asset_id: str):
        try:
            await self.asset_service.delete_asset(asset_id)
            return CustomResponse(
                status_code=200,
                message="Asset deleted successfully"
            )
        except NotExistsError as e:
            return CustomResponse(
                status_code=404,
                message=str(e)
            )
        except Exception as e:
            return CustomResponse(
                status_code=500,
                message="Error deleting asset"
            )

    @custom_logger(logger)
    async def assign_asset(self, assign_data: AssignAssetRequest):
        try:
            await self.asset_service.assign_asset(
            )
            return CustomResponse(
                status_code=200,
                message="Asset assigned successfully"
            )
        except NotExistsError as e:
            return CustomResponse(
                status_code=404,
                message=str(e)
            )
        except AlreadyExistsError as e:
            return CustomResponse(
                status_code=409,
                message=str(e)
            )
        except Exception as e:
            return CustomResponse(
                status_code=500,
                message="Error assigning asset"
            )

    @custom_logger(logger)
    async def unassign_asset(self, unassign_data: UnassignAssetRequest):
        try:
            await self.asset_service.unassign_asset(
                str(unassign_data.asset_id),
                str(unassign_data.user_id)
            )
            return CustomResponse(
                status_code=200,
                message="Asset unassigned successfully"
            )
        except (NotExistsError, NotAssignedError) as e:
            return CustomResponse(
                status_code=404,
                message=str(e)
            )
        except Exception as e:
            return CustomResponse(
                status_code=500,
                message="Error unassigning asset"
            )

    @custom_logger(logger)
    async def assigned_assets(self, user_id: str):
        try:
            assets = await self.asset_service.get_user_assets(user_id)
            return CustomResponse(
                status_code=200,
                message="User assets fetched successfully",
                data=[asset.dict() for asset in assets] if assets else []
            )
        except NotExistsError as e:
            return CustomResponse(
                status_code=404,
                message=str(e)
            )
        except Exception as e:
            return CustomResponse(
                status_code=500,
                message="Error fetching user assets"
            )

    @custom_logger(logger)
    async def assigned_all_assets(self):
        try:
            assets = await self.asset_service.get_all_assigned_assets()
            return CustomResponse(
                status_code=200,
                message="All assigned assets fetched successfully",
                data=[asset.dict() for asset in assets] if assets else []
            )
        except Exception as e:
            return CustomResponse(
                status_code=500,
                message="Error fetching assigned assets"
            )
            return {
                "status_code": 200,
                "message": "All assigned assets fetched successfully",
                "data": [asset.dict() for asset in assets] if assets else []
            }
        except Exception as e:
            raise HTTPException(status_code=500, detail="Error fetching assigned assets")
