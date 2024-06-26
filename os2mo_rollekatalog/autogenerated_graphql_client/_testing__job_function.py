# Generated by ariadne-codegen on 2024-06-20 13:42
# Source: queries.graphql

from typing import List, Optional
from uuid import UUID

from .base_model import BaseModel


class TestingJobFunction(BaseModel):
    facets: "TestingJobFunctionFacets"


class TestingJobFunctionFacets(BaseModel):
    objects: List["TestingJobFunctionFacetsObjects"]


class TestingJobFunctionFacetsObjects(BaseModel):
    current: Optional["TestingJobFunctionFacetsObjectsCurrent"]


class TestingJobFunctionFacetsObjectsCurrent(BaseModel):
    classes: List["TestingJobFunctionFacetsObjectsCurrentClasses"]


class TestingJobFunctionFacetsObjectsCurrentClasses(BaseModel):
    uuid: UUID


TestingJobFunction.update_forward_refs()
TestingJobFunctionFacets.update_forward_refs()
TestingJobFunctionFacetsObjects.update_forward_refs()
TestingJobFunctionFacetsObjectsCurrent.update_forward_refs()
TestingJobFunctionFacetsObjectsCurrentClasses.update_forward_refs()
