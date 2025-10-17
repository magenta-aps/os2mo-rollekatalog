from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import Field

from .base_model import BaseModel


class GetOrgUnit(BaseModel):
    org_units: "GetOrgUnitOrgUnits"


class GetOrgUnitOrgUnits(BaseModel):
    objects: List["GetOrgUnitOrgUnitsObjects"]


class GetOrgUnitOrgUnitsObjects(BaseModel):
    current: Optional["GetOrgUnitOrgUnitsObjectsCurrent"]


class GetOrgUnitOrgUnitsObjectsCurrent(BaseModel):
    uuid: UUID
    name: str
    parent: Optional["GetOrgUnitOrgUnitsObjectsCurrentParent"]
    managers: List["GetOrgUnitOrgUnitsObjectsCurrentManagers"]
    kles: List["GetOrgUnitOrgUnitsObjectsCurrentKles"]


class GetOrgUnitOrgUnitsObjectsCurrentParent(BaseModel):
    uuid: UUID


class GetOrgUnitOrgUnitsObjectsCurrentManagers(BaseModel):
    person: Optional[List["GetOrgUnitOrgUnitsObjectsCurrentManagersPerson"]]


class GetOrgUnitOrgUnitsObjectsCurrentManagersPerson(BaseModel):
    uuid: UUID
    itusers: List["GetOrgUnitOrgUnitsObjectsCurrentManagersPersonItusers"]


class GetOrgUnitOrgUnitsObjectsCurrentManagersPersonItusers(BaseModel):
    uuid: UUID
    user_key: str
    external_id: Optional[str]
    itsystem: "GetOrgUnitOrgUnitsObjectsCurrentManagersPersonItusersItsystem"
    validity: "GetOrgUnitOrgUnitsObjectsCurrentManagersPersonItusersValidity"
    engagements: List[
        "GetOrgUnitOrgUnitsObjectsCurrentManagersPersonItusersEngagements"
    ]


class GetOrgUnitOrgUnitsObjectsCurrentManagersPersonItusersItsystem(BaseModel):
    user_key: str


class GetOrgUnitOrgUnitsObjectsCurrentManagersPersonItusersValidity(BaseModel):
    from_: datetime = Field(alias="from")
    to: Optional[datetime]


class GetOrgUnitOrgUnitsObjectsCurrentManagersPersonItusersEngagements(BaseModel):
    current: Optional[
        "GetOrgUnitOrgUnitsObjectsCurrentManagersPersonItusersEngagementsCurrent"
    ]


class GetOrgUnitOrgUnitsObjectsCurrentManagersPersonItusersEngagementsCurrent(
    BaseModel
):
    org_unit: List[
        "GetOrgUnitOrgUnitsObjectsCurrentManagersPersonItusersEngagementsCurrentOrgUnit"
    ]


class GetOrgUnitOrgUnitsObjectsCurrentManagersPersonItusersEngagementsCurrentOrgUnit(
    BaseModel
):
    uuid: UUID


class GetOrgUnitOrgUnitsObjectsCurrentKles(BaseModel):
    kle_number: List["GetOrgUnitOrgUnitsObjectsCurrentKlesKleNumber"]
    kle_aspects: List["GetOrgUnitOrgUnitsObjectsCurrentKlesKleAspects"]


class GetOrgUnitOrgUnitsObjectsCurrentKlesKleNumber(BaseModel):
    user_key: str


class GetOrgUnitOrgUnitsObjectsCurrentKlesKleAspects(BaseModel):
    scope: Optional[str]


GetOrgUnit.update_forward_refs()
GetOrgUnitOrgUnits.update_forward_refs()
GetOrgUnitOrgUnitsObjects.update_forward_refs()
GetOrgUnitOrgUnitsObjectsCurrent.update_forward_refs()
GetOrgUnitOrgUnitsObjectsCurrentParent.update_forward_refs()
GetOrgUnitOrgUnitsObjectsCurrentManagers.update_forward_refs()
GetOrgUnitOrgUnitsObjectsCurrentManagersPerson.update_forward_refs()
GetOrgUnitOrgUnitsObjectsCurrentManagersPersonItusers.update_forward_refs()
GetOrgUnitOrgUnitsObjectsCurrentManagersPersonItusersItsystem.update_forward_refs()
GetOrgUnitOrgUnitsObjectsCurrentManagersPersonItusersValidity.update_forward_refs()
GetOrgUnitOrgUnitsObjectsCurrentManagersPersonItusersEngagements.update_forward_refs()
GetOrgUnitOrgUnitsObjectsCurrentManagersPersonItusersEngagementsCurrent.update_forward_refs()
GetOrgUnitOrgUnitsObjectsCurrentManagersPersonItusersEngagementsCurrentOrgUnit.update_forward_refs()
GetOrgUnitOrgUnitsObjectsCurrentKles.update_forward_refs()
GetOrgUnitOrgUnitsObjectsCurrentKlesKleNumber.update_forward_refs()
GetOrgUnitOrgUnitsObjectsCurrentKlesKleAspects.update_forward_refs()
