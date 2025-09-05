from typing import List, Optional
from uuid import UUID

from .base_model import BaseModel


class TestingGetEngagementType(BaseModel):
    facets: "TestingGetEngagementTypeFacets"


class TestingGetEngagementTypeFacets(BaseModel):
    objects: List["TestingGetEngagementTypeFacetsObjects"]


class TestingGetEngagementTypeFacetsObjects(BaseModel):
    current: Optional["TestingGetEngagementTypeFacetsObjectsCurrent"]


class TestingGetEngagementTypeFacetsObjectsCurrent(BaseModel):
    classes: List["TestingGetEngagementTypeFacetsObjectsCurrentClasses"]


class TestingGetEngagementTypeFacetsObjectsCurrentClasses(BaseModel):
    uuid: UUID


TestingGetEngagementType.update_forward_refs()
TestingGetEngagementTypeFacets.update_forward_refs()
TestingGetEngagementTypeFacetsObjects.update_forward_refs()
TestingGetEngagementTypeFacetsObjectsCurrent.update_forward_refs()
TestingGetEngagementTypeFacetsObjectsCurrentClasses.update_forward_refs()
