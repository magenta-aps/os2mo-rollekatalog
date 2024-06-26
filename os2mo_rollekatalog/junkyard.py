# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from collections.abc import Generator
from typing import Protocol
from typing import Sequence
from typing import TypeVar
from uuid import UUID

from os2mo_rollekatalog.models import SamAccountName


T = TypeVar("T", covariant=True)


class WillNotSync(Exception):
    def __init__(self, message: str):
        self.message = message


class NoSuitableSamAccount(Exception): ...


class HasUserKey(Protocol):
    user_key: str


class HasUUID(Protocol):
    uuid: UUID


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


def pick_samaccount(itusers: Sequence[HasUserKey]) -> SamAccountName:
    """Pick proper SAM-Account.

    Picking the proper SAM-Account is shared behaviour when creating Users and
    Managers. For now, it is not too well specified. We are waiting for the
    LDAP integration to implement (and decide on) a format.

    This function is essentially just here so whoever implements this in the
    future notice that its for people _and_ managers.
    """
    if len(itusers) == 0:
        raise NoSuitableSamAccount(f"no suitable SAM-Account found for {itusers=}")
    return SamAccountName(itusers[-1].user_key)


def in_org_tree(root_org_unit: UUID, org_unit: OrgWithAncestors) -> bool:
    if root_org_unit == org_unit.uuid:
        return True
    return root_org_unit in {ancestor.uuid for ancestor in org_unit.ancestors}
