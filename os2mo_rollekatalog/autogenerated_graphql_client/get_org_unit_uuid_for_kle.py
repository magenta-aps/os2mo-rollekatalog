from typing import List
from uuid import UUID

from .base_model import BaseModel


class GetOrgUnitUuidForKle(BaseModel):
    kles: "GetOrgUnitUuidForKleKles"


class GetOrgUnitUuidForKleKles(BaseModel):
    objects: List["GetOrgUnitUuidForKleKlesObjects"]


class GetOrgUnitUuidForKleKlesObjects(BaseModel):
    validities: List["GetOrgUnitUuidForKleKlesObjectsValidities"]


class GetOrgUnitUuidForKleKlesObjectsValidities(BaseModel):
    org_unit_uuid: UUID


GetOrgUnitUuidForKle.update_forward_refs()
GetOrgUnitUuidForKleKles.update_forward_refs()
GetOrgUnitUuidForKleKlesObjects.update_forward_refs()
GetOrgUnitUuidForKleKlesObjectsValidities.update_forward_refs()
