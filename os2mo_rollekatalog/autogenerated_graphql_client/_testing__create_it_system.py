from uuid import UUID

from .base_model import BaseModel


class TestingCreateItSystem(BaseModel):
    itsystem_create: "TestingCreateItSystemItsystemCreate"


class TestingCreateItSystemItsystemCreate(BaseModel):
    uuid: UUID


TestingCreateItSystem.update_forward_refs()
TestingCreateItSystemItsystemCreate.update_forward_refs()
