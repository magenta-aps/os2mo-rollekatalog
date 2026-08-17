# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from datetime import datetime
from uuid import UUID
from more_itertools import one

import structlog
from sqlalchemy import delete
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from os2mo_rollekatalog import depends
from os2mo_rollekatalog.junkyard import WillNotSync
from os2mo_rollekatalog.junkyard import is_org_unit_excluded
from os2mo_rollekatalog.junkyard import resolve_samaccounts
from os2mo_rollekatalog.junkyard import select_relevant
from os2mo_rollekatalog.models import Manager
from os2mo_rollekatalog.models import OrgUnit
from os2mo_rollekatalog.models import OrgUnitName
from os2mo_rollekatalog.models import Position
from os2mo_rollekatalog.models import User
from os2mo_rollekatalog.models import SamAccountName


logger = structlog.stdlib.get_logger(__name__)


class ExpectedParent(Exception):
    pass


async def get_org_unit(
    mo: depends.GraphQLClient,
    ad_itsystem_user_keys: list[str],
    fk_itsystem_user_key: str,
    manager_itsystem_user_key: str | None,
    root_org_unit: UUID,
    exclude_org_unit_level: UUID | None,
    exclude_org_units: list[UUID],
    org_unit_uuid: UUID,
    external_roots: list[UUID],
) -> OrgUnit:
    result = await mo.get_org_unit(
        org_unit_uuid,
        [root_org_unit] + external_roots,
        [*ad_itsystem_user_keys, fk_itsystem_user_key],
        datetime.now(),
    )

    if len(result.objects) == 0:
        raise WillNotSync("Org unit is not in root-org tree.")

    org_unit = one(result.objects).current
    if org_unit is None:
        raise WillNotSync("Org unit does not exist now or in the future.")

    if is_org_unit_excluded(org_unit, exclude_org_unit_level, exclude_org_units):
        raise WillNotSync(
            f"Skipping sync for org_unit, due to exclusion filter: {org_unit.uuid}"
        )

    if org_unit.uuid == root_org_unit:
        parent_uuid = None
    elif org_unit.uuid in external_roots:
        parent_uuid = root_org_unit
    else:
        assert org_unit.parent is not None
        parent_uuid = org_unit.parent.uuid

    def get_manager() -> Manager | None:
        """
        Rollekatalog's org unit carries a single manager and MO does not know
        which one to pick, so we pick arbitrarily from the valid ones.

        With MANAGER_ITSYSTEM_USER_KEY set, only accounts in that itsystem
        are considered, so which login carries the manager rights in
        Rollekatalog is configuration, not chance.
        """
        # TODO: MO is getting a manager -> engagement connection, and a primary
        # manager on the org unit. Either would let us report a deliberate
        # manager rather than an arbitrary one. Before building on them, confirm
        # that customers maintain these fields - the fields are
        # only useful to us if the data is actually maintained.
        if len(org_unit.managers) > 1:
            logger.warning(
                "Org unit has multiple managers",
                org_unit=org_unit.uuid,
            )

        for manager in org_unit.managers:
            for person in manager.person or []:
                itusers, samaccounts = resolve_samaccounts(
                    person.itusers, ad_itsystem_user_keys, fk_itsystem_user_key
                )
                for ituser in select_relevant(itusers):
                    if (
                        manager_itsystem_user_key is not None
                        and ituser.itsystem.user_key != manager_itsystem_user_key
                    ):
                        continue
                    extUuid = samaccounts.get(ituser.user_key)
                    if extUuid is None:
                        # No FK-org account to map to, so no extUuid.
                        continue
                    return Manager(uuid=extUuid, userId=SamAccountName(ituser.user_key))
        return None

    manager = get_manager()

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
    periodic_sync: depends.PeriodicSync,
    session: depends.Session,
    ad_itsystem_user_keys: list[str],
    fk_itsystem_user_key: str,
    manager_itsystem_user_key: str | None,
    root_org_unit: UUID,
    exclude_org_unit_level: UUID | None,
    exclude_org_units: list[UUID],
    org_unit_uuid: UUID,
    external_roots: list[UUID],
) -> None:
    try:
        org_unit = await get_org_unit(
            mo,
            ad_itsystem_user_keys,
            fk_itsystem_user_key,
            manager_itsystem_user_key,
            root_org_unit,
            exclude_org_unit_level or None,
            exclude_org_units,
            org_unit_uuid,
            external_roots,
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
                periodic_sync,
                session,
                ad_itsystem_user_keys,
                fk_itsystem_user_key,
                manager_itsystem_user_key,
                root_org_unit,
                exclude_org_unit_level,
                exclude_org_units,
                child_uuid,
                external_roots,
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
