from uuid import UUID

from .base_model import BaseModel


class TestingUpdateItUserEngagements(BaseModel):
    ituser_update: "TestingUpdateItUserEngagementsItuserUpdate"


class TestingUpdateItUserEngagementsItuserUpdate(BaseModel):
    uuid: UUID


TestingUpdateItUserEngagements.update_forward_refs()
TestingUpdateItUserEngagementsItuserUpdate.update_forward_refs()
