from typing import List
from uuid import UUID

from .base_model import BaseModel


class TestingGetManagerType(BaseModel):
    classes: "TestingGetManagerTypeClasses"


class TestingGetManagerTypeClasses(BaseModel):
    objects: List["TestingGetManagerTypeClassesObjects"]


class TestingGetManagerTypeClassesObjects(BaseModel):
    uuid: UUID


TestingGetManagerType.update_forward_refs()
TestingGetManagerTypeClasses.update_forward_refs()
TestingGetManagerTypeClassesObjects.update_forward_refs()
