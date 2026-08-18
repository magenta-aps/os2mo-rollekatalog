from uuid import UUID

from .base_model import BaseModel


class TestingUpdateOrgUnit(BaseModel):
    org_unit_update: "TestingUpdateOrgUnitOrgUnitUpdate"


class TestingUpdateOrgUnitOrgUnitUpdate(BaseModel):
    uuid: UUID


TestingUpdateOrgUnit.update_forward_refs()
TestingUpdateOrgUnitOrgUnitUpdate.update_forward_refs()
