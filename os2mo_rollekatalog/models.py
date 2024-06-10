# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from typing import NewType
from uuid import UUID

from pydantic import BaseModel
from pydantic import EmailStr


SamAccountName = NewType("SamAccountName", str)
Name = NewType("Name", str)


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
