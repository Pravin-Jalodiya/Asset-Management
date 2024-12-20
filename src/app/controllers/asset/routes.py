from fastapi import APIRouter, Depends, Request

from src.app.controllers.asset.handlers import AssetHandler
from src.app.middleware.middleware import auth_middleware
from src.app.services.asset_service import AssetService
from src.app.models.request_objects import AssetRequest, AssignAssetRequest, UnassignAssetRequest

def create_asset_routes(asset_service: AssetService) -> APIRouter:
    router = APIRouter(tags=["assets"])
    asset_handler = AssetHandler.create(asset_service)
    
    # Add dependencies for auth
    router.dependencies = [Depends(auth_middleware)]

    @router.get("/assets")
    async def get_assets(request: Request):
        return await asset_handler.get_assets(request)

    @router.post("/add-asset")
    async def add_asset(request: Request,request_data: AssetRequest):
        return await asset_handler.add_asset(request, request_data)

    @router.post("/assign-asset")
    async def assign_asset(request: Request, request_data: AssignAssetRequest):
        return await asset_handler.assign_asset(request, request_data)

    @router.post("/unassign-asset")
    async def unassign_asset(request_data: UnassignAssetRequest):
        return await asset_handler.unassign_asset(request_data)

    @router.get("/assigned-assets/all")
    async def assigned_all_assets(request: Request):
        return await asset_handler.assigned_all_assets(request)

    @router.get("/assigned-assets/{user_id}")
    async def assigned_assets(user_id: str):
        return await asset_handler.assigned_assets(user_id)

    @router.delete("/asset/{asset_id}")
    async def delete_asset(request: Request, asset_id: str):
        return await asset_handler.delete_asset(request, asset_id)

    return router
