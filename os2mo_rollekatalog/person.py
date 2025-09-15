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
from os2mo_rollekatalog.models import Name
from os2mo_rollekatalog.models import Position
from os2mo_rollekatalog.models import User


logger = structlog.stdlib.get_logger(__name__)


async def get_person(
    mo: depends.GraphQLClient,
    ldap_client: depends.LDAPClient,
    itsystem_user_keys: list[str],
    root_org_unit: UUID,
    person_uuid: UUID,
    prefer_nickname: bool,
    sync_titles: bool,
) -> list[User]:
    result = await mo.get_person(
        person_uuid, root_org_unit, datetime.now(), itsystem_user_keys
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

    users = []
    itusers = resolve_samaccounts(mo_person.itusers, itsystem_user_keys)
    if not itusers:
        # Do not sync users without an AD account
        raise WillNotSync("No SAM Account")

    for ituser in itusers:
        positions = []
        if ituser.engagements:
            for engagement in ituser.engagements:
                for org_unit in engagement.org_unit:
                    positions.append(
                        Position(
                            name=engagement.job_function.name,
                            orgUnitUuid=org_unit.uuid,
                            titleUuid=engagement.job_function.uuid
                            if sync_titles
                            else None,
                        )
                    )
        if len(positions) == 0:
            # Do not sync users without any positions
            raise WillNotSync("User has no valid positions (engagements)")

        users.append(
            User(
                # TODO: remove mo_person
                person=mo_person.uuid,
                extUuid=UUID(ituser.external_id) or mo_person.uuid,
                userId=ituser.user_key,
                name=name,
                email=email,
                positions=positions,
            )
        )
    return users


async def fetch_person_from_db(
    session: depends.Session, uuid: UUID
) -> list[User] | None:
    stmt = (
        select(User)
        .options(selectinload(User.positions))
        .where(User.person == uuid)
        .join(User.positions)
    )
    scalar_result = await session.scalars(stmt)
    users = scalar_result.all()

    return [user for user in users]


async def sync_person(
    mo: depends.GraphQLClient,
    ldap_client: depends.LDAPClient,
    periodic_sync: depends.PeriodicSync,
    session: depends.Session,
    itsystem_user_keys: list[str],
    root_org_unit: UUID,
    person_uuid: UUID,
    prefer_nickname: bool,
    sync_titles: bool,
) -> None:
    try:
        users = await get_person(
            mo,
            ldap_client,
            itsystem_user_keys,
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

    for user in users:
        dbusers = await fetch_person_from_db(session, user.person)

        ext_map = {u.extUuid: u for u in (users or [])}
        db_map = {u.extUuid: u for u in (dbusers or [])}

        ext_keys = set(ext_map.keys())
        db_keys = set(db_map.keys())

        print(ext_keys)
        print(db_keys)

        to_add = ext_keys - db_keys
        to_remove = db_keys - ext_keys
        to_check = ext_keys & db_keys

        print("to_add")
        print(to_add)
        print("to_remove")
        print(to_remove)
        print("to_check")
        print(to_check)

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

        # add new accounts
        for key in to_add:
            new_user = ext_map[key]
            session.add(new_user)
            logger.info(
                "Add new user",
                uuid=new_user.extUuid,
                name=new_user.name,
                samaccount=new_user.userId,
            )

        # update changed accounts
        for key in to_check:
            incoming = ext_map[key]
            existing = db_map[key]

            if incoming == existing:
                logger.info(
                    "User unchanged",
                    uuid=incoming.extUuid,
                    name=incoming.name,
                    samaccount=incoming.userId,
                )
                continue

            existing.person = incoming.person
            existing.name = incoming.name
            existing.extUuid = incoming.extUuid
            existing.userId = incoming.userId
            existing.userId = incoming.userId
            existing.email = incoming.email
            existing.positions = incoming.positions

            logger.info(
                "Update user",
                uuid=incoming.extUuid,
                name=incoming.name,
                samaccount=incoming.userId,
            )
    # for user in users:
    #     dbusers = await fetch_person_from_db(
    #         session, user.person
    #     )
    #     if dbusers:
    #         for dbuser in dbusers:
    #             print("2222222222222222222222222")
    #             print(dbuser)
    #             print(user)
    #
    #             raise
    #             if user == dbuser:
    #                 print("USER IS THE SAME")
    #                 continue  # no changes
    #
    #             # update existing user
    #             await session.delete(dbuser)
    #             session.add(user)
    #             logger.info(
    #                 "Update user", uuid=user.extUuid, name=user.name, samaccount=user.userId
    #             )
    #
    #     else:
    #         print("NO USER")
    #         raise
    #         session.add(user)
    #         logger.info(
    #             "Add new user",
    #             uuid=user.extUuid,
    #             name=user.name,
    #             samaccount=user.userId,
    #         )
    #         continue

    periodic_sync.sync_soon()
