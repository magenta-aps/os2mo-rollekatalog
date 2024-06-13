# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from contextlib import suppress
from datetime import datetime
from uuid import UUID

from os2mo_rollekatalog import depends
from os2mo_rollekatalog.junkyard import NoSuitableSamAccount
from os2mo_rollekatalog.junkyard import flatten_validities
from os2mo_rollekatalog.junkyard import in_org_tree
from os2mo_rollekatalog.junkyard import pick_samaccount
from os2mo_rollekatalog.models import Manager
from os2mo_rollekatalog.models import OrgUnit
from os2mo_rollekatalog.models import OrgUnitName


class ExpectedParent(Exception):
    pass


async def get_org_unit(
    mo: depends.GraphQLClient,
    itsystem_user_key: str,
    root_org_unit: UUID,
    org_unit_uuid: UUID,
) -> OrgUnit | None:
    result = await mo.get_org_unit(itsystem_user_key, datetime.now(), org_unit_uuid)

    if (
        len(result.org_units.objects) == 0
        or result.org_units.objects[0].current is None
    ):
        return None

    org_unit = result.org_units.objects[0].current

    if not in_org_tree(root_org_unit, org_unit):
        return None

    if org_unit.uuid == root_org_unit:
        # Make this one the root in Rollekatalog
        parent_uuid = None
    elif org_unit.parent is None:
        # This should never happen, as we know `root_org_unit` is in ancestors.
        raise ExpectedParent(f"org_unit.parent is None for {org_unit.uuid=}")
    else:
        # Otherwise, we have a known parent
        parent_uuid = org_unit.parent.uuid

    def get_manager() -> Manager | None:
        for manager in flatten_validities(result.managers):
            # Check that manager position is not vacant
            if manager.person is None:
                continue
            for person in manager.person:
                with suppress(NoSuitableSamAccount):
                    return Manager(
                        uuid=person.uuid,
                        userId=pick_samaccount(person.itusers),
                    )
        return None

    manager = get_manager()

    kle_performing = []
    kle_interests = []
    for kle in flatten_validities(result.kles):
        for aspect in kle.kle_aspects:
            if aspect.scope == "INDSIGT":
                kle_interests.append(kle.kle_number.user_key)
            if aspect.scope == "UDFOERENDE":
                kle_performing.append(kle.kle_number.user_key)

    return OrgUnit(
        uuid=org_unit.uuid,
        name=OrgUnitName(org_unit.name),
        parentOrgUnitUuid=parent_uuid,
        manager=manager,
        klePerforming=kle_performing,
        kleInterest=kle_interests,
    )


async def sync_org_unit(
    mo: depends.GraphQLClient,
    cache: dict[UUID, OrgUnit],
    itsystem_user_key: str,
    root_org_unit: UUID,
    org_unit_uuid: UUID,
) -> None:
    org_unit = await get_org_unit(
        mo,
        itsystem_user_key,
        root_org_unit,
        org_unit_uuid,
    )
    if org_unit is None:
        return
    cache[org_unit_uuid] = org_unit
