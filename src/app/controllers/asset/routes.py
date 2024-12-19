from fastapi import APIRouter, Depends
from typing import List

from src.app.controllers.asset.handlers import AssetHandler
from src.app.middleware.middleware import auth_middleware
from src.app.services.asset_service import AssetService
from src.app.models.request_objects import AssetRequest, AssignAssetRequest, UnassignAssetRequest

def create_asset_routes(asset_service: AssetService) -> APIRouter:
    router = APIRouter(prefix="/assets", tags=["assets"])
    asset_handler = AssetHandler.create(asset_service)
    
    # Add dependencies for auth
    router.dependencies = [Depends(auth_middleware)]

    @router.get("/")
    async def get_assets():
        return await asset_handler.get_assets()

    @router.post("/")
    async def add_asset(request: AssetRequest):
        return await asset_handler.add_asset(request)

    @router.delete("/{asset_id}")
    async def delete_asset(asset_id: str):
        return await asset_handler.delete_asset(asset_id)

    @router.post("/assign")
    async def assign_asset(request: AssignAssetRequest):
        return await asset_handler.assign_asset(request)

    @router.post("/unassign")
    async def unassign_asset(request: UnassignAssetRequest):
        return await asset_handler.unassign_asset(request)

    @router.get("/assigned/{user_id}")
    async def assigned_assets(user_id: str):
        return await asset_handler.assigned_assets(user_id)

    @router.get("/assigned")
    async def assigned_all_assets():
        return await asset_handler.assigned_all_assets()

    return router
