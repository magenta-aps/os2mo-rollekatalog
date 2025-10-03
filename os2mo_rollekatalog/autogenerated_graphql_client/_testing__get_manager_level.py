from typing import List
from uuid import UUID

from .base_model import BaseModel


class TestingGetManagerLevel(BaseModel):
    classes: "TestingGetManagerLevelClasses"


class TestingGetManagerLevelClasses(BaseModel):
    objects: List["TestingGetManagerLevelClassesObjects"]


class TestingGetManagerLevelClassesObjects(BaseModel):
    uuid: UUID


TestingGetManagerLevel.update_forward_refs()
TestingGetManagerLevelClasses.update_forward_refs()
TestingGetManagerLevelClassesObjects.update_forward_refs()
