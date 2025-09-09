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
from os2mo_rollekatalog.junkyard import NoSuitableSamAccount
from os2mo_rollekatalog.junkyard import WillNotSync
from os2mo_rollekatalog.junkyard import pick_samaccount
from os2mo_rollekatalog.models import Name
from os2mo_rollekatalog.models import Position
from os2mo_rollekatalog.models import User


logger = structlog.stdlib.get_logger(__name__)


async def get_person(
    mo: depends.GraphQLClient,
    ldap_client: depends.LDAPClient,
    itsystem_user_key: str,
    root_org_unit: UUID,
    person_uuid: UUID,
    prefer_nickname: bool,
    sync_titles: bool,
) -> User:
    result = await mo.get_person(
        person_uuid, root_org_unit, itsystem_user_key, datetime.now()
    )

    if len(result.objects) == 0 or one(result.objects).current is None:
        raise WillNotSync("Not found. Strange.")

    mo_person = one(result.objects).current

    if mo_person is None:
        raise
    try:
        # Behaviour of the old integration 🤷
        email = list(mo_person.addresses)[-1].value
    except IndexError:
        email = None

    if prefer_nickname and mo_person.nickname:
        name = Name(mo_person.nickname)
    else:
        name = Name(mo_person.name)

    try:
        sam_account_name = await pick_samaccount(
            ldap_client, mo_person.uuid, mo_person.itusers
        )
    except NoSuitableSamAccount:
        # Do not sync users without an AD account
        raise WillNotSync("No SAM Account")

    positions = []
    for engagement in mo_person.engagements:
        for org_unit in engagement.org_unit:
            positions.append(
                Position(
                    name=engagement.job_function.name,
                    orgUnitUuid=org_unit.uuid,
                    titleUuid=engagement.job_function.uuid if sync_titles else None,
                )
            )
    if len(positions) == 0:
        # Do not sync users without any positions
        raise WillNotSync("User has no valid positions (engagements)")

    return User(
        extUuid=mo_person.uuid,
        userId=sam_account_name,
        name=name,
        email=email,
        positions=positions,
    )


async def fetch_person_from_db(session: depends.Session, uuid: UUID) -> User | None:
    return await session.scalar(
        select(User)
        .options(selectinload(User.positions))
        .where(User.extUuid == uuid)
        .join(User.positions)
    )


async def sync_person(
    mo: depends.GraphQLClient,
    ldap_client: depends.LDAPClient,
    periodic_sync: depends.PeriodicSync,
    session: depends.Session,
    itsystem_user_key: str,
    root_org_unit: UUID,
    person_uuid: UUID,
    prefer_nickname: bool,
    sync_titles: bool,
) -> None:
    try:
        user = await get_person(
            mo,
            ldap_client,
            itsystem_user_key,
            root_org_unit,
            person_uuid,
            prefer_nickname,
            sync_titles,
        )
    except WillNotSync:
        delete_result = await session.execute(
            delete(User).where(User.extUuid == person_uuid)
        )
        if delete_result.rowcount > 0:
            logger.info("Remove user", uuid=person_uuid)
            periodic_sync.sync_soon()
        return

    dbuser = await fetch_person_from_db(session, person_uuid)

    if dbuser is None:
        logger.info(
            "Add new user", uuid=user.extUuid, name=user.name, samaccount=user.userId
        )
        session.add(user)
        periodic_sync.sync_soon()
        return

    if user == dbuser:
        return

    logger.info(
        "Update user", uuid=user.extUuid, name=user.name, samaccount=user.userId
    )
    await session.delete(dbuser)
    session.add(user)
    periodic_sync.sync_soon()
