from enum import Enum


class Role(Enum):
    USER = 'user'
    ADMIN = "admin"


class AssetStatus(Enum):
    AVAILABLE = 'available'
    ASSIGNED = 'assigned'
    RETIRED = 'retired'


class Department(Enum):
    CLOUD = 'CLOUD PLATFORM'
    DEV_PLAT = 'DEV PLATFORM'
    BUSINESS = 'BUSINESS PLATFORM'
    CUSTOMER = 'CUSTOMER PLATFROM'
