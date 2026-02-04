from typing import List, Optional
from uuid import UUID

from .base_model import BaseModel


class TestingGetMitID(BaseModel):
    facets: "TestingGetMitIDFacets"


class TestingGetMitIDFacets(BaseModel):
    objects: List["TestingGetMitIDFacetsObjects"]


class TestingGetMitIDFacetsObjects(BaseModel):
    current: Optional["TestingGetMitIDFacetsObjectsCurrent"]


class TestingGetMitIDFacetsObjectsCurrent(BaseModel):
    classes: List["TestingGetMitIDFacetsObjectsCurrentClasses"]


class TestingGetMitIDFacetsObjectsCurrentClasses(BaseModel):
    uuid: UUID
    user_key: str


TestingGetMitID.update_forward_refs()
TestingGetMitIDFacets.update_forward_refs()
TestingGetMitIDFacetsObjects.update_forward_refs()
TestingGetMitIDFacetsObjectsCurrent.update_forward_refs()
TestingGetMitIDFacetsObjectsCurrentClasses.update_forward_refs()
