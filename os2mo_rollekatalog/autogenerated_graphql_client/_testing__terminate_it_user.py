from uuid import UUID

from .base_model import BaseModel


class TestingTerminateItUser(BaseModel):
    ituser_terminate: "TestingTerminateItUserItuserTerminate"


class TestingTerminateItUserItuserTerminate(BaseModel):
    uuid: UUID


TestingTerminateItUser.update_forward_refs()
TestingTerminateItUserItuserTerminate.update_forward_refs()
