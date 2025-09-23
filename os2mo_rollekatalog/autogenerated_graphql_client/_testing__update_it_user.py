from uuid import UUID

from .base_model import BaseModel


class TestingUpdateItUser(BaseModel):
    ituser_update: "TestingUpdateItUserItuserUpdate"


class TestingUpdateItUserItuserUpdate(BaseModel):
    uuid: UUID


TestingUpdateItUser.update_forward_refs()
TestingUpdateItUserItuserUpdate.update_forward_refs()
