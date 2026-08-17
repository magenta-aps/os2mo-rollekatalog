from typing import List, Optional
from uuid import UUID

from .base_model import BaseModel


class TestingGetEmailEmployee(BaseModel):
    facets: "TestingGetEmailEmployeeFacets"


class TestingGetEmailEmployeeFacets(BaseModel):
    objects: List["TestingGetEmailEmployeeFacetsObjects"]


class TestingGetEmailEmployeeFacetsObjects(BaseModel):
    current: Optional["TestingGetEmailEmployeeFacetsObjectsCurrent"]


class TestingGetEmailEmployeeFacetsObjectsCurrent(BaseModel):
    classes: List["TestingGetEmailEmployeeFacetsObjectsCurrentClasses"]


class TestingGetEmailEmployeeFacetsObjectsCurrentClasses(BaseModel):
    uuid: UUID
    user_key: str


TestingGetEmailEmployee.update_forward_refs()
TestingGetEmailEmployeeFacets.update_forward_refs()
TestingGetEmailEmployeeFacetsObjects.update_forward_refs()
TestingGetEmailEmployeeFacetsObjectsCurrent.update_forward_refs()
TestingGetEmailEmployeeFacetsObjectsCurrentClasses.update_forward_refs()
