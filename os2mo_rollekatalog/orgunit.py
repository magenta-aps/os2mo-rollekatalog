# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from contextlib import suppress
from datetime import datetime
from uuid import UUID
from more_itertools import one

import structlog
from sqlalchemy import delete
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from os2mo_rollekatalog import depends
from os2mo_rollekatalog.junkyard import NoSuitableSamAccount
from os2mo_rollekatalog.junkyard import WillNotSync
from os2mo_rollekatalog.junkyard import pick_samaccount
from os2mo_rollekatalog.models import Manager
from os2mo_rollekatalog.models import OrgUnit
from os2mo_rollekatalog.models import OrgUnitName
from os2mo_rollekatalog.models import Position
from os2mo_rollekatalog.models import User


logger = structlog.stdlib.get_logger(__name__)


class ExpectedParent(Exception):
    pass


async def get_org_unit(
    mo: depends.GraphQLClient,
    ldap_client: depends.LDAPClient,
    itsystem_user_keys: list[str],
    root_org_unit: UUID,
    org_unit_uuid: UUID,
) -> OrgUnit:
    result = await mo.get_org_unit(
        org_unit_uuid, root_org_unit, datetime.now(), itsystem_user_keys
    )

    if len(result.objects) == 0:
        raise WillNotSync("Org unit is not in root-org tree.")

    org_unit = one(result.objects).current
    if org_unit is None:
        raise WillNotSync("Org unit does not exist now or in the future.")

    if org_unit.uuid == root_org_unit or org_unit.parent is None:
        parent_uuid = None
    else:
        parent_uuid = org_unit.parent.uuid

    async def get_manager() -> Manager | None:
        for manager in org_unit.managers:
            # Check that manager position is not vacant
            if manager.person is None:
                continue
            for person in manager.person:
                with suppress(NoSuitableSamAccount):
                    return Manager(
                        uuid=person.uuid,
                        userId=(
                            await pick_samaccount(
                                ldap_client, person.uuid, person.itusers
                            )
                        ),
                    )
        return None

    manager = await get_manager()

    kle_performing = set()
    kle_interests = set()
    for kle in org_unit.kles:
        for aspect in kle.kle_aspects:
            if aspect.scope == "INFORMERET":
                kle_interests |= {n.user_key for n in kle.kle_number}
            if aspect.scope == "UDFOERENDE":
                kle_performing |= {n.user_key for n in kle.kle_number}

    return OrgUnit(
        uuid=org_unit.uuid,
        name=OrgUnitName(org_unit.name),
        parentOrgUnitUuid=parent_uuid,
        manager=manager,
        klePerforming=list(kle_performing),
        kleInterest=list(kle_interests),
    )


async def fetch_org_unit_from_db(
    session: depends.Session, uuid: UUID
) -> OrgUnit | None:
    return await session.scalar(
        select(OrgUnit)
        .options(selectinload(OrgUnit.manager))
        .where(OrgUnit.uuid == uuid)
    )


async def sync_org_unit(
    mo: depends.GraphQLClient,
    ldap_client: depends.LDAPClient,
    periodic_sync: depends.PeriodicSync,
    session: depends.Session,
    itsystem_user_keys: list[str],
    root_org_unit: UUID,
    org_unit_uuid: UUID,
) -> None:
    try:
        org_unit = await get_org_unit(
            mo,
            ldap_client,
            itsystem_user_keys,
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
        # TODO: these invariants should be upheld by the db and cascade deleted
        # Remove positions that are no longer in a valid org unit:
        await session.execute(
            delete(Position).where(Position.orgUnitUuid == org_unit_uuid)
        )
        # Remove users that no longer have >= 1 position:
        users_without_positions = (
            select(User.id).outerjoin(Position).where(Position.id.is_(None))
        )
        await session.execute(delete(User).where(User.id.in_(users_without_positions)))
        # Remove org units that points to the removed unit (recursively (to
        # uphold the other invariants)):
        for child_uuid in await session.scalars(
            select(OrgUnit.uuid).where(OrgUnit.parentOrgUnitUuid == org_unit_uuid)
        ):
            await sync_org_unit(
                mo,
                ldap_client,
                periodic_sync,
                session,
                itsystem_user_keys,
                root_org_unit,
                child_uuid,
            )

        periodic_sync.sync_soon()
        return

    dborg = await fetch_org_unit_from_db(session, org_unit.uuid)

    if dborg is None:
        logger.info("Add new org unit", uuid=org_unit.uuid, name=org_unit.name)
        session.add(org_unit)
        periodic_sync.sync_soon()
        return

    if org_unit == dborg:
        return

    logger.info("Update org unit", uuid=org_unit.uuid, name=org_unit.name)
    if dborg.manager:
        await session.delete(dborg.manager)
    await session.delete(dborg)
    await session.flush()
    session.add(org_unit)
    periodic_sync.sync_soon()
