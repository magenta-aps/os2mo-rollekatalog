from uuid import UUID

from .base_model import BaseModel


class TestingRenameOrgUnit(BaseModel):
    org_unit_update: "TestingRenameOrgUnitOrgUnitUpdate"


class TestingRenameOrgUnitOrgUnitUpdate(BaseModel):
    uuid: UUID


TestingRenameOrgUnit.update_forward_refs()
TestingRenameOrgUnitOrgUnitUpdate.update_forward_refs()
