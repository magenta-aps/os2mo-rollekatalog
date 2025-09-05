from uuid import UUID

from .base_model import BaseModel


class TestingCreateOrgUnitRoot(BaseModel):
    org_unit_create: "TestingCreateOrgUnitRootOrgUnitCreate"


class TestingCreateOrgUnitRootOrgUnitCreate(BaseModel):
    uuid: UUID


TestingCreateOrgUnitRoot.update_forward_refs()
TestingCreateOrgUnitRootOrgUnitCreate.update_forward_refs()
