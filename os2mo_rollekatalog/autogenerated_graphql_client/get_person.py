# Generated by ariadne-codegen on 2024-06-20 16:41
# Source: queries.graphql

from typing import List, Optional
from uuid import UUID

from .base_model import BaseModel


class GetPerson(BaseModel):
    employees: "GetPersonEmployees"
    addresses: "GetPersonAddresses"
    itusers: "GetPersonItusers"
    engagements: "GetPersonEngagements"


class GetPersonEmployees(BaseModel):
    objects: List["GetPersonEmployeesObjects"]


class GetPersonEmployeesObjects(BaseModel):
    current: Optional["GetPersonEmployeesObjectsCurrent"]


class GetPersonEmployeesObjectsCurrent(BaseModel):
    uuid: UUID
    user_key: str
    nickname: str
    name: str


class GetPersonAddresses(BaseModel):
    objects: List["GetPersonAddressesObjects"]


class GetPersonAddressesObjects(BaseModel):
    validities: List["GetPersonAddressesObjectsValidities"]


class GetPersonAddressesObjectsValidities(BaseModel):
    uuid: UUID
    value: str


class GetPersonItusers(BaseModel):
    objects: List["GetPersonItusersObjects"]


class GetPersonItusersObjects(BaseModel):
    validities: List["GetPersonItusersObjectsValidities"]


class GetPersonItusersObjectsValidities(BaseModel):
    user_key: str


class GetPersonEngagements(BaseModel):
    objects: List["GetPersonEngagementsObjects"]


class GetPersonEngagementsObjects(BaseModel):
    validities: List["GetPersonEngagementsObjectsValidities"]


class GetPersonEngagementsObjectsValidities(BaseModel):
    org_unit: List["GetPersonEngagementsObjectsValiditiesOrgUnit"]
    job_function: "GetPersonEngagementsObjectsValiditiesJobFunction"


class GetPersonEngagementsObjectsValiditiesOrgUnit(BaseModel):
    uuid: UUID
    ancestors: List["GetPersonEngagementsObjectsValiditiesOrgUnitAncestors"]


class GetPersonEngagementsObjectsValiditiesOrgUnitAncestors(BaseModel):
    uuid: UUID


class GetPersonEngagementsObjectsValiditiesJobFunction(BaseModel):
    name: str
    uuid: UUID


GetPerson.update_forward_refs()
GetPersonEmployees.update_forward_refs()
GetPersonEmployeesObjects.update_forward_refs()
GetPersonEmployeesObjectsCurrent.update_forward_refs()
GetPersonAddresses.update_forward_refs()
GetPersonAddressesObjects.update_forward_refs()
GetPersonAddressesObjectsValidities.update_forward_refs()
GetPersonItusers.update_forward_refs()
GetPersonItusersObjects.update_forward_refs()
GetPersonItusersObjectsValidities.update_forward_refs()
GetPersonEngagements.update_forward_refs()
GetPersonEngagementsObjects.update_forward_refs()
GetPersonEngagementsObjectsValidities.update_forward_refs()
GetPersonEngagementsObjectsValiditiesOrgUnit.update_forward_refs()
GetPersonEngagementsObjectsValiditiesOrgUnitAncestors.update_forward_refs()
GetPersonEngagementsObjectsValiditiesJobFunction.update_forward_refs()
