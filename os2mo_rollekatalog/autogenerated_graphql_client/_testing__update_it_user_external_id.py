from uuid import UUID

from .base_model import BaseModel


class TestingUpdateItUserExternalId(BaseModel):
    ituser_update: "TestingUpdateItUserExternalIdItuserUpdate"


class TestingUpdateItUserExternalIdItuserUpdate(BaseModel):
    uuid: UUID


TestingUpdateItUserExternalId.update_forward_refs()
TestingUpdateItUserExternalIdItuserUpdate.update_forward_refs()
