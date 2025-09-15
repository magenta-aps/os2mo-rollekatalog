# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from typing import NewType
from uuid import UUID

from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from sqlalchemy import ForeignKey
from sqlalchemy import String
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped


SamAccountName = NewType("SamAccountName", str)
Name = NewType("Name", str)
OrgUnitName = NewType("OrgUnitName", str)
KLE = NewType("KLE", str)


# Titles are synced on-demand and not part of the persistent state
class Title(BaseModel):
    uuid: UUID
    user_key: str

    def to_rollekatalog_payload(self):
        result = {"name": self.user_key, "uuid": self.uuid}
        return jsonable_encoder(result)


class Base(DeclarativeBase):
    type_annotation_map = {
        SamAccountName: String,
        Name: String,
        OrgUnitName: String,
        KLE: String,
        list[KLE]: ARRAY(String),
    }


class Position(Base):
    __tablename__ = "position"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    # Not a relation, as we could learn about the user before the orgunit
    orgUnitUuid: Mapped[UUID]
    titleUuid: Mapped[UUID | None]

    user_id: Mapped[int] = mapped_column(ForeignKey("user.id", ondelete="CASCADE"))

    def __repr__(self) -> str:
        return f"Position({self.name=}, {self.orgUnitUuid=}, {self.titleUuid=})"

    def __eq__(self, other: object) -> bool:
        if isinstance(other, Position):
            return (
                self.name == other.name
                and self.orgUnitUuid == other.orgUnitUuid
                and self.titleUuid == other.titleUuid
            )
        raise NotImplementedError()

    def __hash__(self):
        return hash((self.name, self.orgUnitUuid, self.titleUuid))

    def to_rollekatalog_payload(self):
        result = {"name": self.name, "orgUnitUuid": self.orgUnitUuid}
        if self.titleUuid is not None:
            result["titleUuid"] = self.titleUuid
        return jsonable_encoder(result)


class User(Base):
    __tablename__ = "user"

    id: Mapped[int] = mapped_column(primary_key=True)
    person: Mapped[UUID]
    extUuid: Mapped[UUID]
    userId: Mapped[SamAccountName]
    name: Mapped[Name]
    email: Mapped[str | None]
    positions: Mapped[list[Position]] = relationship(
        single_parent=True, cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"User({self.person=}, {self.extUuid=}, {self.userId=}, {self.name=}, {self.email=}, {self.positions=})"

    def __eq__(self, other: object) -> bool:
        if isinstance(other, User):
            return (
                self.person == other.person
                and self.extUuid == other.extUuid
                and self.userId == other.userId
                and self.name == other.name
                and self.email == other.email
                and self.positions == other.positions
            )
        raise NotImplementedError()

    def __hash__(self):
        # Positions must be a frozenset to be hashable
        return hash(
            (
                self.person,
                self.extUuid,
                self.userId,
                self.name,
                self.email,
                frozenset(self.positions),
            )
        )

    def to_rollekatalog_payload(self):
        return jsonable_encoder(
            {
                "person": self.person,
                "extUuid": self.extUuid,
                "userId": self.userId,
                "name": self.name,
                "email": self.email,
                "positions": [pos.to_rollekatalog_payload() for pos in self.positions],
            }
        )


class Manager(Base):
    __tablename__ = "manager"

    id: Mapped[int] = mapped_column(primary_key=True)
    uuid: Mapped[UUID]
    userId: Mapped[SamAccountName]

    org_unit_id: Mapped[int] = mapped_column(
        ForeignKey("orgunit.id", ondelete="CASCADE")
    )

    def __repr__(self) -> str:
        return f"Manager({self.uuid=}, {self.userId=})"

    def __eq__(self, other: object) -> bool:
        if isinstance(other, Manager):
            return self.uuid == other.uuid and self.userId == other.userId
        if other is None:
            return False
        raise NotImplementedError()

    def to_rollekatalog_payload(self):
        return jsonable_encoder(
            {"uuid": self.uuid, "userId": self.userId, "org_unit_id": self.org_unit_id}
        )


class OrgUnit(Base):
    __tablename__ = "orgunit"

    id: Mapped[int] = mapped_column(primary_key=True)
    uuid: Mapped[UUID] = mapped_column(unique=True)
    name: Mapped[OrgUnitName]
    # Not a relation, as we could learn about the child before the parent
    parentOrgUnitUuid: Mapped[UUID | None]
    manager: Mapped[Manager | None] = relationship(cascade="all, delete-orphan")
    klePerforming: Mapped[list[KLE]]
    kleInterest: Mapped[list[KLE]]

    def __repr__(self) -> str:
        return f"OrgUnit({self.uuid=}, {self.name=}, {self.parentOrgUnitUuid=}, {self.manager=}, {self.klePerforming=}, {self.kleInterest=})"

    def __eq__(self, other: object) -> bool:
        if isinstance(other, OrgUnit):
            return (
                self.uuid == other.uuid
                and self.name == other.name
                and self.parentOrgUnitUuid == other.parentOrgUnitUuid
                and self.manager == other.manager
                and self.klePerforming == other.klePerforming
                and self.kleInterest == other.kleInterest
            )
        raise NotImplementedError()

    def to_rollekatalog_payload(self):
        return jsonable_encoder(
            {
                "uuid": self.uuid,
                "name": self.name,
                "parentOrgUnitUuid": self.parentOrgUnitUuid,
                "manager": self.manager,
                "klePerforming": self.klePerforming,
                "kleInterest": self.kleInterest,
            }
        )
