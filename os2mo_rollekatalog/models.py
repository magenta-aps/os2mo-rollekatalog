# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from typing import NewType
from uuid import UUID

from pydantic import BaseModel
from pydantic import EmailStr


SamAccountName = NewType("SamAccountName", str)
Name = NewType("Name", str)
OrgUnitName = NewType("OrgUnitName", str)
KLE = NewType("KLE", str)


class Title(BaseModel):
    uuid: UUID
    user_key: str


class Position(BaseModel):
    name: str
    orgUnitUuid: UUID
    titleUuid: UUID | None


class User(BaseModel):
    extUuid: UUID
    userId: SamAccountName
    name: Name
    email: EmailStr | None
    # If empty position, do not sync
    positions: list[Position]


class Manager(BaseModel):
    uuid: UUID
    userId: SamAccountName


class OrgUnit(BaseModel):
    uuid: UUID
    name: OrgUnitName
    parentOrgUnitUuid: UUID | None
    manager: Manager | None
    klePerforming: list[KLE]
    kleInterest: list[KLE]


OrgUnitCache = NewType("OrgUnitCache", dict[UUID, OrgUnit])
UserCache = NewType("UserCache", dict[UUID, User])
