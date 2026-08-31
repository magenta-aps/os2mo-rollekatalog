from typing import List, Optional
from uuid import UUID

from .base_model import BaseModel


class GetFunctions(BaseModel):
    classes: "GetFunctionsClasses"


class GetFunctionsClasses(BaseModel):
    objects: List["GetFunctionsClassesObjects"]


class GetFunctionsClassesObjects(BaseModel):
    current: Optional["GetFunctionsClassesObjectsCurrent"]


class GetFunctionsClassesObjectsCurrent(BaseModel):
    name: str
    uuid: UUID


GetFunctions.update_forward_refs()
GetFunctionsClasses.update_forward_refs()
GetFunctionsClassesObjects.update_forward_refs()
GetFunctionsClassesObjectsCurrent.update_forward_refs()
