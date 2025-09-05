from typing import List
from uuid import UUID

from .base_model import BaseModel


class GetOrgUnitUuidForManager(BaseModel):
    managers: "GetOrgUnitUuidForManagerManagers"


class GetOrgUnitUuidForManagerManagers(BaseModel):
    objects: List["GetOrgUnitUuidForManagerManagersObjects"]


class GetOrgUnitUuidForManagerManagersObjects(BaseModel):
    validities: List["GetOrgUnitUuidForManagerManagersObjectsValidities"]


class GetOrgUnitUuidForManagerManagersObjectsValidities(BaseModel):
    org_unit_uuid: UUID


GetOrgUnitUuidForManager.update_forward_refs()
GetOrgUnitUuidForManagerManagers.update_forward_refs()
GetOrgUnitUuidForManagerManagersObjects.update_forward_refs()
GetOrgUnitUuidForManagerManagersObjectsValidities.update_forward_refs()
