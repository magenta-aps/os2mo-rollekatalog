from typing import List, Optional
from uuid import UUID

from .base_model import BaseModel


class GetPerson(BaseModel):
    employees: "GetPersonEmployees"


class GetPersonEmployees(BaseModel):
    objects: List["GetPersonEmployeesObjects"]


class GetPersonEmployeesObjects(BaseModel):
    current: Optional["GetPersonEmployeesObjectsCurrent"]


class GetPersonEmployeesObjectsCurrent(BaseModel):
    uuid: UUID
    user_key: str
    nickname: str
    name: str
    addresses: List["GetPersonEmployeesObjectsCurrentAddresses"]
    itusers: List["GetPersonEmployeesObjectsCurrentItusers"]
    engagements: List["GetPersonEmployeesObjectsCurrentEngagements"]


class GetPersonEmployeesObjectsCurrentAddresses(BaseModel):
    uuid: UUID
    value: str


class GetPersonEmployeesObjectsCurrentItusers(BaseModel):
    user_key: str
    external_id: Optional[str]
    itsystem: "GetPersonEmployeesObjectsCurrentItusersItsystem"


class GetPersonEmployeesObjectsCurrentItusersItsystem(BaseModel):
    user_key: str


class GetPersonEmployeesObjectsCurrentEngagements(BaseModel):
    org_unit: List["GetPersonEmployeesObjectsCurrentEngagementsOrgUnit"]
    job_function: "GetPersonEmployeesObjectsCurrentEngagementsJobFunction"


class GetPersonEmployeesObjectsCurrentEngagementsOrgUnit(BaseModel):
    uuid: UUID


class GetPersonEmployeesObjectsCurrentEngagementsJobFunction(BaseModel):
    name: str
    uuid: UUID


GetPerson.update_forward_refs()
GetPersonEmployees.update_forward_refs()
GetPersonEmployeesObjects.update_forward_refs()
GetPersonEmployeesObjectsCurrent.update_forward_refs()
GetPersonEmployeesObjectsCurrentAddresses.update_forward_refs()
GetPersonEmployeesObjectsCurrentItusers.update_forward_refs()
GetPersonEmployeesObjectsCurrentItusersItsystem.update_forward_refs()
GetPersonEmployeesObjectsCurrentEngagements.update_forward_refs()
GetPersonEmployeesObjectsCurrentEngagementsOrgUnit.update_forward_refs()
GetPersonEmployeesObjectsCurrentEngagementsJobFunction.update_forward_refs()
