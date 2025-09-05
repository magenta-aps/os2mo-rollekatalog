from typing import List
from uuid import UUID

from .base_model import BaseModel


class RefreshAll(BaseModel):
    employee_refresh: "RefreshAllEmployeeRefresh"
    org_unit_refresh: "RefreshAllOrgUnitRefresh"
    class_refresh: "RefreshAllClassRefresh"


class RefreshAllEmployeeRefresh(BaseModel):
    objects: List[UUID]


class RefreshAllOrgUnitRefresh(BaseModel):
    objects: List[UUID]


class RefreshAllClassRefresh(BaseModel):
    objects: List[UUID]


RefreshAll.update_forward_refs()
RefreshAllEmployeeRefresh.update_forward_refs()
RefreshAllOrgUnitRefresh.update_forward_refs()
RefreshAllClassRefresh.update_forward_refs()
