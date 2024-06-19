# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from contextlib import suppress
from datetime import datetime
from uuid import UUID

import structlog
from sqlalchemy import delete
from sqlalchemy import select
from sqlalchemy import Row
from sqlalchemy.orm import selectinload

from os2mo_rollekatalog import depends
from os2mo_rollekatalog.junkyard import NoSuitableSamAccount
from os2mo_rollekatalog.junkyard import WillNotSync
from os2mo_rollekatalog.junkyard import flatten_validities
from os2mo_rollekatalog.junkyard import in_org_tree
from os2mo_rollekatalog.junkyard import pick_samaccount
from os2mo_rollekatalog.models import Manager
from os2mo_rollekatalog.models import OrgUnit
from os2mo_rollekatalog.models import OrgUnitName
from os2mo_rollekatalog.models import Position
from os2mo_rollekatalog.models import User


logger = structlog.get_logger(__name__)


class ExpectedParent(Exception):
    pass


async def get_org_unit(
    mo: depends.GraphQLClient,
    itsystem_user_key: str,
    root_org_unit: UUID,
    org_unit_uuid: UUID,
) -> OrgUnit:
    result = await mo.get_org_unit(itsystem_user_key, datetime.now(), org_unit_uuid)

    if (
        len(result.org_units.objects) == 0
        or result.org_units.objects[0].current is None
    ):
        raise WillNotSync("Not found. Strange.")

    org_unit = result.org_units.objects[0].current

    if not in_org_tree(root_org_unit, org_unit):
        raise WillNotSync(f"Not in tree, must be below {root_org_unit}")

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
    rollekatalog: depends.Rollekatalog,
    session: depends.Session,
    itsystem_user_key: str,
    root_org_unit: UUID,
    org_unit_uuid: UUID,
) -> None:
    try:
        org_unit = await get_org_unit(
            mo,
            itsystem_user_key,
            root_org_unit,
            org_unit_uuid,
        )
    except WillNotSync:
        delete_result = await session.execute(
            delete(OrgUnit).where(OrgUnit.uuid == org_unit_uuid)
        )
        if delete_result.rowcount == 0:
            return  # No changes.

        logger.info("Remove org unit", uuid=org_unit_uuid)
        await session.execute(
            delete(Position).where(Position.orgUnitUuid == org_unit_uuid)
        )
        users_without_positions = (
            select(User.id).outerjoin(Position).where(Position.id == None)  # noqa: E711
        )
        await session.execute(delete(User).where(User.id.in_(users_without_positions)))

        rollekatalog.sync_soon()
        return

    result = await session.execute(
        select(OrgUnit)
        .options(selectinload(OrgUnit.manager))
        .where(OrgUnit.uuid == org_unit.uuid)
    )
    dborg: Row[tuple[OrgUnit]] | None = result.one_or_none()

    if dborg is None:
        logger.info("Add new org unit", uuid=org_unit.uuid, name=org_unit.name)
        session.add(org_unit)
        rollekatalog.sync_soon()
        return

    if org_unit == dborg[0]:
        return

    logger.info("Update org unit", uuid=org_unit.uuid, name=org_unit.name)
    if dborg[0].manager:
        await session.delete(dborg[0].manager)
    await session.delete(dborg[0])
    session.add(org_unit)
    rollekatalog.sync_soon()
