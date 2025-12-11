from uuid import UUID

from .base_model import BaseModel


class TestingCreateOrgUnitType(BaseModel):
    class_create: "TestingCreateOrgUnitTypeClassCreate"


class TestingCreateOrgUnitTypeClassCreate(BaseModel):
    uuid: UUID


TestingCreateOrgUnitType.update_forward_refs()
TestingCreateOrgUnitTypeClassCreate.update_forward_refs()
