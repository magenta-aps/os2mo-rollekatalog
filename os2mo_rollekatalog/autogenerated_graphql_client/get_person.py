from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import Field

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


class GetPersonEmployeesObjectsCurrentAddresses(BaseModel):
    uuid: UUID
    value: str


class GetPersonEmployeesObjectsCurrentItusers(BaseModel):
    uuid: UUID
    user_key: str
    external_id: Optional[str]
    itsystem: "GetPersonEmployeesObjectsCurrentItusersItsystem"
    validity: "GetPersonEmployeesObjectsCurrentItusersValidity"
    engagements: List["GetPersonEmployeesObjectsCurrentItusersEngagements"]


class GetPersonEmployeesObjectsCurrentItusersItsystem(BaseModel):
    user_key: str


class GetPersonEmployeesObjectsCurrentItusersValidity(BaseModel):
    from_: datetime = Field(alias="from")
    to: Optional[datetime]


class GetPersonEmployeesObjectsCurrentItusersEngagements(BaseModel):
    current: Optional["GetPersonEmployeesObjectsCurrentItusersEngagementsCurrent"]


class GetPersonEmployeesObjectsCurrentItusersEngagementsCurrent(BaseModel):
    org_unit: List["GetPersonEmployeesObjectsCurrentItusersEngagementsCurrentOrgUnit"]
    job_function: "GetPersonEmployeesObjectsCurrentItusersEngagementsCurrentJobFunction"


class GetPersonEmployeesObjectsCurrentItusersEngagementsCurrentOrgUnit(BaseModel):
    uuid: UUID
    validity: "GetPersonEmployeesObjectsCurrentItusersEngagementsCurrentOrgUnitValidity"


class GetPersonEmployeesObjectsCurrentItusersEngagementsCurrentOrgUnitValidity(
    BaseModel
):
    from_: datetime = Field(alias="from")
    to: Optional[datetime]


class GetPersonEmployeesObjectsCurrentItusersEngagementsCurrentJobFunction(BaseModel):
    name: str
    uuid: UUID


GetPerson.update_forward_refs()
GetPersonEmployees.update_forward_refs()
GetPersonEmployeesObjects.update_forward_refs()
GetPersonEmployeesObjectsCurrent.update_forward_refs()
GetPersonEmployeesObjectsCurrentAddresses.update_forward_refs()
GetPersonEmployeesObjectsCurrentItusers.update_forward_refs()
GetPersonEmployeesObjectsCurrentItusersItsystem.update_forward_refs()
GetPersonEmployeesObjectsCurrentItusersValidity.update_forward_refs()
GetPersonEmployeesObjectsCurrentItusersEngagements.update_forward_refs()
GetPersonEmployeesObjectsCurrentItusersEngagementsCurrent.update_forward_refs()
GetPersonEmployeesObjectsCurrentItusersEngagementsCurrentOrgUnit.update_forward_refs()
GetPersonEmployeesObjectsCurrentItusersEngagementsCurrentOrgUnitValidity.update_forward_refs()
GetPersonEmployeesObjectsCurrentItusersEngagementsCurrentJobFunction.update_forward_refs()
