from uuid import UUID

from .base_model import BaseModel


class TestingUpdateClass(BaseModel):
    class_update: "TestingUpdateClassClassUpdate"


class TestingUpdateClassClassUpdate(BaseModel):
    uuid: UUID


TestingUpdateClass.update_forward_refs()
TestingUpdateClassClassUpdate.update_forward_refs()
