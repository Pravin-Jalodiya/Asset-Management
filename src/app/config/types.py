from enum import Enum

class Role(Enum):
    USER = 'user'
    ADMIN = "admin"

class AssetStatus(Enum):
    AVAILABLE = 'available'
    ASSIGNED = 'assigned'
    RETIRED = 'retired'

class Department(Enum):
    CLOUD = 'cloud platform'
    DEV_PLAT = 'dev platform'
    BUSINESS = 'business platform'
    CUSTOMER = 'customer platform'