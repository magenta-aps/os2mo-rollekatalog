# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from collections.abc import Generator
from dataclasses import dataclass
from typing import Protocol
from typing import Sequence
from typing import TypeVar
from typing import Optional
from uuid import UUID
from datetime import datetime
from zoneinfo import ZoneInfo
from collections import defaultdict
from more_itertools import one
import structlog

logger = structlog.stdlib.get_logger(__name__)


T = TypeVar("T", covariant=True)


class WillNotSync(Exception):
    def __init__(self, message: str):
        self.message = message


class NoSuitableSamAccount(Exception): ...


class HasUserKey(Protocol):
    user_key: str


class HasUUID(Protocol):
    uuid: UUID


class ITSystem(Protocol):
    @property
    def user_key(self) -> str: ...


class HasITSystem(Protocol):
    @property
    def itsystem(self) -> ITSystem: ...


class HasExternalID(Protocol):
    external_id: Optional[str]


class OrgWithAncestors(HasUUID, Protocol):
    @property
    def ancestors(self) -> Sequence[HasUUID]: ...


class Classified(HasUUID, Protocol):
    """An org unit as far as the exclusion rules care about it."""

    @property
    def org_unit_level(self) -> Optional[HasUUID]: ...

    @property
    def org_unit_type(self) -> Optional[HasUUID]: ...


class ClassifiedWithAncestors(Classified, Protocol):
    @property
    def ancestors(self) -> Sequence[Classified]: ...


@dataclass(frozen=True)
class OrgUnitExclusions:
    """Org units the customer does not want in Rollekatalog.

    Three ways of pointing at a unit, because customers think about it in
    three ways: "no units on this level", "no units of this type", and "not
    that particular subtree" (MED-organisation, error- and conversion
    departments, and so on).

    Excluding a unit excludes its descendants too. Rollekatalog has no way to
    represent a unit whose parent is missing, so keeping the children would
    leave dangling parentOrgUnitUuid references.
    """

    levels: frozenset[UUID] = frozenset()
    types: frozenset[UUID] = frozenset()
    uuids: frozenset[UUID] = frozenset()

    def __bool__(self) -> bool:
        return bool(self.levels or self.types or self.uuids)

    def _own_reason(self, unit: Classified) -> str | None:
        if unit.uuid in self.uuids:
            return "unit is excluded by uuid"
        if unit.org_unit_level and unit.org_unit_level.uuid in self.levels:
            return f"unit has excluded org_unit_level {unit.org_unit_level.uuid}"
        if unit.org_unit_type and unit.org_unit_type.uuid in self.types:
            return f"unit has excluded org_unit_type {unit.org_unit_type.uuid}"
        return None

    def reason_to_exclude(self, unit: ClassifiedWithAncestors) -> str | None:
        """Why this unit should not be synced, or None if it should be."""
        own = self._own_reason(unit)
        if own is not None:
            return own
        for ancestor in unit.ancestors:
            reason = self._own_reason(ancestor)
            if reason is not None:
                return f"ancestor {ancestor.uuid} is excluded: {reason}"
        return None


class HasValidities(Protocol[T]):
    @property
    def validities(self) -> Sequence[T]: ...


class HasObjects(Protocol[T]):
    @property
    def objects(self) -> Sequence[T]: ...


def flatten_validities(
    something: HasObjects[HasValidities[T]],
) -> Generator[T, None, None]:
    for obj in something.objects:
        for validity in obj.validities:
            yield validity


class ITUser(HasUUID, HasUserKey, HasExternalID, HasITSystem, Protocol):
    """
    Protocol that represents any IT-user object we can resolve SAM accounts for.
    """


def resolve_samaccounts(
    itusers: Sequence[ITUser],
    ad_itsystem_user_keys: list[str],
    fk_itsystem_user_key: str,
) -> tuple[list[ITUser], dict[str, UUID]]:
    """
    Resolve SAM accounts for IT-users.

    For each AD IT-user, look up a matching FK IT-user.
    Build a mapping {ad.user_key: resolved_external_id}.

    Multiple AD-like itsystems are supported (e.g. a regular AD and a
    separate "Skole-AD"); they are all mapped to the FK itsystem the
    same way.

    Returns:
        (ad_itusers, samaccounts)
        - ad_itusers: list of AD IT-users
        - samaccounts: dict mapping AD user_key -> external_id (resolved if match found)
    """
    ad_itusers = [it for it in itusers if it.itsystem.user_key in ad_itsystem_user_keys]
    if not ad_itusers:
        return [], {}

    fk_itusers = {
        it.user_key: UUID(it.external_id)
        for it in itusers
        if it.itsystem.user_key == fk_itsystem_user_key and it.external_id
    }
    samaccounts: dict[str, UUID] = {}
    for ad in ad_itusers:
        if ad.external_id and ad.external_id in fk_itusers:
            samaccounts[ad.user_key] = fk_itusers[ad.external_id]

    return ad_itusers, samaccounts


def select_relevant(
    objects: list,
) -> list:
    """
    Pick the current version of each object if available,
    otherwise pick the earliest future version.
    """

    now = datetime.now(ZoneInfo("Europe/Copenhagen")).date()
    grouped: dict[UUID, list] = defaultdict(list)
    for object in objects:
        grouped[object.uuid].append(object)

    result: list = []

    for uuid, versions in grouped.items():
        # Pick current ituser
        current = [
            version
            for version in versions
            if version.validity.from_.date() <= now
            and (version.validity.to is None or now < version.validity.to.date())
        ]

        if current:
            result.append(one(current))
            continue

        # Otherwise pick the soonest future version, if any
        future = [
            version for version in versions if version.validity.from_.date() > now
        ]
        if future:
            result.append(min(future, key=lambda version: version.validity.from_))
        else:
            logger.info(
                f"No current or future found for {uuid} with versions: {versions}"
            )
            continue

    return result


def select_preferred(objects: list):
    """Pick the single most relevant object among candidates.

    Prefer a currently valid object; among several, the newest wins: the one
    whose validity history starts latest. A version's own start date cannot
    tell, since editing an object splits its validity. If nothing is valid
    yet, pick the soonest future one. Expects full validity history.
    """
    now = datetime.now(ZoneInfo("Europe/Copenhagen")).date()
    first_from: dict[UUID, datetime] = {}
    for obj in objects:
        if obj.uuid not in first_from or obj.validity.from_ < first_from[obj.uuid]:
            first_from[obj.uuid] = obj.validity.from_
    # select_relevant expects current/future input; drop expired versions.
    active = [
        obj
        for obj in objects
        if obj.validity.to is None or now < obj.validity.to.date()
    ]
    relevant = select_relevant(active)
    current = [obj for obj in relevant if obj.validity.from_.date() <= now]
    # Date ties break by uuid, in the same direction in both branches so the
    # winner doesn't flip when a future object becomes current.
    if current:
        return max(current, key=lambda obj: (first_from[obj.uuid], obj.uuid))
    return min(
        relevant, key=lambda obj: (obj.validity.from_, -obj.uuid.int), default=None
    )
