# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from collections.abc import Generator
from typing import NewType
from typing import Protocol
from typing import Sequence
from typing import TypeVar
from uuid import UUID

from httpx import AsyncClient
from pydantic import AnyHttpUrl

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


LDAPClient = NewType("LDAPClient", AsyncClient)


def create_ldap_client(ldap_url: AnyHttpUrl) -> LDAPClient:
    return LDAPClient(AsyncClient(base_url=ldap_url))


async def pick_samaccount(
    ldap_client: LDAPClient | None, employee_uuid: UUID, itusers: Sequence[HasUserKey]
) -> SamAccountName:
    """Pick proper SAM-Account.

    Picking the proper SAM-Account is shared behaviour when creating Users and
    Managers. This function is essentially just here so whoever implements this
    in the future notice that its for people _and_ managers.

    It also implements a "strategy pattern". For now we use ask the LDAP
    integration for the sam account (this is what the old integration did).
    When the LDAP integration supports multiple accounts, we need to pick the
    proper one from MO.
    """
    if ldap_client is None:
        # This is where the support for multiple IT users is supposed to go.
        # https://redmine.magenta.dk/issues/65188.
        if len(itusers) == 0:
            raise NoSuitableSamAccount(f"no suitable SAM-Account found for {itusers=}")
        return SamAccountName(itusers[-1].user_key)
    else:
        # This behaviour is compatible with the old integration. We ask the
        # LDAP integration to resolve the sam account name for the employee.
        r = await ldap_client.get("/CPRUUID", params={"uuid": str(employee_uuid)})
        if r.status_code == 404:
            raise NoSuitableSamAccount(
                f"According to the LDAP integration {employee_uuid=} has no SAM-Account"
            )
        r.raise_for_status()
        j = r.json()
        samaccount = j["username"]
        if not samaccount:
            raise NoSuitableSamAccount(
                f"No SAM-Account for {employee_uuid=}, got '{samaccount}'"
            )
        return SamAccountName(samaccount)


def in_org_tree(root_org_unit: UUID, org_unit: OrgWithAncestors) -> bool:
    if root_org_unit == org_unit.uuid:
        return True
    return root_org_unit in {ancestor.uuid for ancestor in org_unit.ancestors}
