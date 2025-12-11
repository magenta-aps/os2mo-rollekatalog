from typing import List
from uuid import UUID

from .base_model import BaseModel


class TestingGetOrgUnitTypeFacetUUID(BaseModel):
    facets: "TestingGetOrgUnitTypeFacetUUIDFacets"


class TestingGetOrgUnitTypeFacetUUIDFacets(BaseModel):
    objects: List["TestingGetOrgUnitTypeFacetUUIDFacetsObjects"]


class TestingGetOrgUnitTypeFacetUUIDFacetsObjects(BaseModel):
    uuid: UUID


TestingGetOrgUnitTypeFacetUUID.update_forward_refs()
TestingGetOrgUnitTypeFacetUUIDFacets.update_forward_refs()
TestingGetOrgUnitTypeFacetUUIDFacetsObjects.update_forward_refs()
