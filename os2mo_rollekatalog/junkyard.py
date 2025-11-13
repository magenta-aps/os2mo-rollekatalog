# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from collections.abc import Generator
from typing import NewType
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

from httpx import AsyncClient
from pydantic import AnyHttpUrl

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


LDAPClient = NewType("LDAPClient", AsyncClient)


def create_ldap_client(ldap_url: AnyHttpUrl) -> LDAPClient:
    return LDAPClient(AsyncClient(base_url=ldap_url))


def resolve_samaccounts(
    itusers: Sequence[ITUser],
    ad_itsystem_user_key: str,
    fk_itsystem_user_key: str,
) -> tuple[list[ITUser], dict[str, UUID]]:
    """
    Resolve SAM accounts for IT-users.

    For each AD IT-user, look up a matching FK IT-user.
    Build a mapping {ad.user_key: resolved_external_id}.

    Returns:
        (ad_itusers, samaccounts)
        - ad_itusers: list of AD IT-users
        - samaccounts: dict mapping AD user_key -> external_id (resolved if match found)
    """
    ad_itusers = [it for it in itusers if it.itsystem.user_key == ad_itsystem_user_key]
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
