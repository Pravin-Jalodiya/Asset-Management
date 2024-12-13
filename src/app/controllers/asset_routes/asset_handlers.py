from flask import Blueprint, request, jsonify, g
from werkzeug.routing import ValidationError
from dataclasses import dataclass

from AssetManagement.src.app.models.user import User
from AssetManagement.src.app.services.asset_service import AssetService
from AssetManagement.src.app.services.user_service import UserService
from AssetManagement.src.app.utils.logger.custom_logger import custom_logger
from AssetManagement.src.app.utils.utils import Utils
from AssetManagement.src.app.utils.validators.validators import Validators
from AssetManagement.src.app.utils.logger.logger import Logger


@dataclass
class UserHandler:
    asset_service: AssetService
    logger = Logger()

    @classmethod
    def create(cls, asset_service):
        return cls(asset_service)

