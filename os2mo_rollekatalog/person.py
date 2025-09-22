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
from os2mo_rollekatalog.junkyard import resolve_samaccounts
from os2mo_rollekatalog.junkyard import select_relevant
from os2mo_rollekatalog.models import Name
from os2mo_rollekatalog.models import Position
from os2mo_rollekatalog.models import User


logger = structlog.stdlib.get_logger(__name__)


async def get_person(
    mo: depends.GraphQLClient,
    ldap_client: depends.LDAPClient,
    ad_itsystem_user_key: str,
    fk_itsystem_user_key: str,
    root_org_unit: UUID,
    person_uuid: UUID,
    prefer_nickname: bool,
    sync_titles: bool,
) -> list[User]:
    result = await mo.get_person(
        person_uuid,
        root_org_unit,
        ad_itsystem_user_key,
        fk_itsystem_user_key,
        datetime.now(),
    )

    if len(result.objects) == 0 or one(result.objects).current is None:
        raise WillNotSync("Not found. Strange.")

    mo_person = one(result.objects).current

    if mo_person is None:
        raise WillNotSync("Not found")
    try:
        # Behaviour of the old integration 🤷
        email = list(mo_person.addresses)[-1].value
    except IndexError:
        email = None

    if prefer_nickname and mo_person.nickname:
        name = Name(mo_person.nickname)
    else:
        name = Name(mo_person.name)

    users = []
    itusers, samaccounts = resolve_samaccounts(
        mo_person.itusers, ad_itsystem_user_key, fk_itsystem_user_key
    )

    if not itusers:
        # Do not sync users without an AD account
        raise WillNotSync("No SAM Account")

    relevant_itusers = select_relevant(itusers)

    for ituser in relevant_itusers:
        extUuid = samaccounts.get(ituser.user_key)
        if extUuid is None:
            continue

        positions = [
            Position(
                name=eng.current.job_function.name,
                orgUnitUuid=one(select_relevant(eng.current.org_unit)).uuid,
                titleUuid=eng.current.job_function.uuid if sync_titles else None,
            )
            for eng in ituser.engagements or []
            if eng.current and eng.current.org_unit
        ]
        if len(positions) == 0:
            # Skip itusers without valid engagements
            continue

        users.append(
            User(
                person=mo_person.uuid,
                extUuid=extUuid,
                userId=ituser.user_key,
                name=name,
                email=email,
                positions=positions,
            )
        )
    return users


async def fetch_users_from_db(session: depends.Session, uuid: UUID) -> list[User]:
    stmt = select(User).options(selectinload(User.positions)).where(User.person == uuid)
    scalar_result = await session.scalars(stmt)
    users = scalar_result.all()

    return [user for user in users]


async def sync_person(
    mo: depends.GraphQLClient,
    ldap_client: depends.LDAPClient,
    periodic_sync: depends.PeriodicSync,
    session: depends.Session,
    ad_itsystem_user_key: str,
    fk_itsystem_user_key: str,
    root_org_unit: UUID,
    person_uuid: UUID,
    prefer_nickname: bool,
    sync_titles: bool,
) -> None:
    try:
        users = await get_person(
            mo,
            ldap_client,
            ad_itsystem_user_key,
            fk_itsystem_user_key,
            root_org_unit,
            person_uuid,
            prefer_nickname,
            sync_titles,
        )
    except WillNotSync:
        delete_result = await session.execute(
            delete(User).where(User.person == person_uuid)
        )
        if delete_result.rowcount > 0:
            logger.info("Remove user", uuid=person_uuid)
            periodic_sync.sync_soon()
        return

    mo_map = {u.extUuid: u for u in users}
    dbusers = await fetch_users_from_db(session, person_uuid)
    db_map = {u.extUuid: u for u in dbusers}

    mo_keys = set(mo_map.keys())
    db_keys = set(db_map.keys())

    to_add = mo_keys - db_keys
    to_remove = db_keys - mo_keys
    to_check = mo_keys & db_keys

    # remove missing accounts
    for key in to_remove:
        old_user = db_map[key]
        await session.delete(old_user)
        logger.info(
            "Remove user",
            uuid=old_user.extUuid,
            name=old_user.name,
            samaccount=old_user.userId,
        )
        periodic_sync.sync_soon()

    # add new accounts
    for key in to_add:
        new_user = mo_map[key]
        session.add(new_user)
        logger.info(
            "Add new user",
            uuid=new_user.extUuid,
            name=new_user.name,
            samaccount=new_user.userId,
        )
        periodic_sync.sync_soon()

    # update changed accounts
    for key in to_check:
        incoming = mo_map[key]
        existing = db_map[key]

        if incoming == existing:
            logger.info(
                "User unchanged",
                uuid=existing.extUuid,
                name=existing.name,
                samaccount=existing.userId,
            )
            continue

        await session.delete(existing)
        await session.flush()
        session.add(incoming)
        periodic_sync.sync_soon()
        logger.info(
            "Update user",
            uuid=incoming.extUuid,
            name=incoming.name,
            samaccount=incoming.userId,
        )
