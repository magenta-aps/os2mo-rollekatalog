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
    email: List["GetPersonEmployeesObjectsCurrentEmail"]
    mitid: List["GetPersonEmployeesObjectsCurrentMitid"]
    itusers: List["GetPersonEmployeesObjectsCurrentItusers"]


class GetPersonEmployeesObjectsCurrentEmail(BaseModel):
    uuid: UUID
    value: str
    validity: "GetPersonEmployeesObjectsCurrentEmailValidity"
    ituser: List["GetPersonEmployeesObjectsCurrentEmailItuser"]


class GetPersonEmployeesObjectsCurrentEmailValidity(BaseModel):
    from_: datetime = Field(alias="from")
    to: Optional[datetime]


class GetPersonEmployeesObjectsCurrentEmailItuser(BaseModel):
    uuid: UUID


class GetPersonEmployeesObjectsCurrentMitid(BaseModel):
    value: str
    ituser: List["GetPersonEmployeesObjectsCurrentMitidItuser"]


class GetPersonEmployeesObjectsCurrentMitidItuser(BaseModel):
    uuid: UUID


class GetPersonEmployeesObjectsCurrentItusers(BaseModel):
    uuid: UUID
    user_key: str
    external_id: Optional[str]
    itsystem: "GetPersonEmployeesObjectsCurrentItusersItsystem"
    validity: "GetPersonEmployeesObjectsCurrentItusersValidity"
    addresses: List["GetPersonEmployeesObjectsCurrentItusersAddresses"]
    engagements: List["GetPersonEmployeesObjectsCurrentItusersEngagements"]


class GetPersonEmployeesObjectsCurrentItusersItsystem(BaseModel):
    user_key: str


class GetPersonEmployeesObjectsCurrentItusersValidity(BaseModel):
    from_: datetime = Field(alias="from")
    to: Optional[datetime]


class GetPersonEmployeesObjectsCurrentItusersAddresses(BaseModel):
    uuid: UUID
    value: str
    validity: "GetPersonEmployeesObjectsCurrentItusersAddressesValidity"


class GetPersonEmployeesObjectsCurrentItusersAddressesValidity(BaseModel):
    from_: datetime = Field(alias="from")
    to: Optional[datetime]


class GetPersonEmployeesObjectsCurrentItusersEngagements(BaseModel):
    validities: List["GetPersonEmployeesObjectsCurrentItusersEngagementsValidities"]


class GetPersonEmployeesObjectsCurrentItusersEngagementsValidities(BaseModel):
    uuid: UUID
    validity: "GetPersonEmployeesObjectsCurrentItusersEngagementsValiditiesValidity"
    org_unit: List[
        "GetPersonEmployeesObjectsCurrentItusersEngagementsValiditiesOrgUnit"
    ]
    job_function: (
        "GetPersonEmployeesObjectsCurrentItusersEngagementsValiditiesJobFunction"
    )


class GetPersonEmployeesObjectsCurrentItusersEngagementsValiditiesValidity(BaseModel):
    from_: datetime = Field(alias="from")
    to: Optional[datetime]


class GetPersonEmployeesObjectsCurrentItusersEngagementsValiditiesOrgUnit(BaseModel):
    uuid: UUID
    org_unit_level: Optional[
        "GetPersonEmployeesObjectsCurrentItusersEngagementsValiditiesOrgUnitOrgUnitLevel"
    ]
    ancestors: List[
        "GetPersonEmployeesObjectsCurrentItusersEngagementsValiditiesOrgUnitAncestors"
    ]
    validity: (
        "GetPersonEmployeesObjectsCurrentItusersEngagementsValiditiesOrgUnitValidity"
    )


class GetPersonEmployeesObjectsCurrentItusersEngagementsValiditiesOrgUnitOrgUnitLevel(
    BaseModel
):
    uuid: UUID


class GetPersonEmployeesObjectsCurrentItusersEngagementsValiditiesOrgUnitAncestors(
    BaseModel
):
    uuid: UUID
    org_unit_level: Optional[
        "GetPersonEmployeesObjectsCurrentItusersEngagementsValiditiesOrgUnitAncestorsOrgUnitLevel"
    ]


class GetPersonEmployeesObjectsCurrentItusersEngagementsValiditiesOrgUnitAncestorsOrgUnitLevel(
    BaseModel
):
    uuid: UUID


class GetPersonEmployeesObjectsCurrentItusersEngagementsValiditiesOrgUnitValidity(
    BaseModel
):
    from_: datetime = Field(alias="from")
    to: Optional[datetime]


class GetPersonEmployeesObjectsCurrentItusersEngagementsValiditiesJobFunction(
    BaseModel
):
    name: str
    uuid: UUID


GetPerson.update_forward_refs()
GetPersonEmployees.update_forward_refs()
GetPersonEmployeesObjects.update_forward_refs()
GetPersonEmployeesObjectsCurrent.update_forward_refs()
GetPersonEmployeesObjectsCurrentEmail.update_forward_refs()
GetPersonEmployeesObjectsCurrentEmailValidity.update_forward_refs()
GetPersonEmployeesObjectsCurrentEmailItuser.update_forward_refs()
GetPersonEmployeesObjectsCurrentMitid.update_forward_refs()
GetPersonEmployeesObjectsCurrentMitidItuser.update_forward_refs()
GetPersonEmployeesObjectsCurrentItusers.update_forward_refs()
GetPersonEmployeesObjectsCurrentItusersItsystem.update_forward_refs()
GetPersonEmployeesObjectsCurrentItusersValidity.update_forward_refs()
GetPersonEmployeesObjectsCurrentItusersAddresses.update_forward_refs()
GetPersonEmployeesObjectsCurrentItusersAddressesValidity.update_forward_refs()
GetPersonEmployeesObjectsCurrentItusersEngagements.update_forward_refs()
GetPersonEmployeesObjectsCurrentItusersEngagementsValidities.update_forward_refs()
GetPersonEmployeesObjectsCurrentItusersEngagementsValiditiesValidity.update_forward_refs()
GetPersonEmployeesObjectsCurrentItusersEngagementsValiditiesOrgUnit.update_forward_refs()
GetPersonEmployeesObjectsCurrentItusersEngagementsValiditiesOrgUnitOrgUnitLevel.update_forward_refs()
GetPersonEmployeesObjectsCurrentItusersEngagementsValiditiesOrgUnitAncestors.update_forward_refs()
GetPersonEmployeesObjectsCurrentItusersEngagementsValiditiesOrgUnitAncestorsOrgUnitLevel.update_forward_refs()
GetPersonEmployeesObjectsCurrentItusersEngagementsValiditiesOrgUnitValidity.update_forward_refs()
GetPersonEmployeesObjectsCurrentItusersEngagementsValiditiesJobFunction.update_forward_refs()
