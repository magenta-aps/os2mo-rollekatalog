# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
import hashlib
from datetime import datetime
from uuid import UUID
from more_itertools import one

import structlog
from sqlalchemy import delete
from sqlalchemy import select
from sqlalchemy import text
from sqlalchemy.orm import selectinload

from os2mo_rollekatalog import depends
from os2mo_rollekatalog.junkyard import WillNotSync
from os2mo_rollekatalog.junkyard import is_org_unit_excluded
from os2mo_rollekatalog.junkyard import resolve_samaccounts
from os2mo_rollekatalog.junkyard import select_preferred
from os2mo_rollekatalog.junkyard import select_relevant
from os2mo_rollekatalog.models import Name
from os2mo_rollekatalog.models import Position
from os2mo_rollekatalog.models import User
from os2mo_rollekatalog.models import UserFunction


logger = structlog.stdlib.get_logger(__name__)


async def get_person(
    mo: depends.GraphQLClient,
    ad_itsystem_user_keys: list[str],
    fk_itsystem_user_key: str,
    employee_email_user_key: str,
    mit_id_user_key: str,
    root_org_unit: UUID,
    person_uuid: UUID,
    prefer_nickname: bool,
    sync_titles: bool,
    sync_functions: bool,
    sync_association_types: list[UUID] | None,
    external_roots: list[UUID],
    exclude_org_unit_level: UUID | None,
    exclude_org_units: list[UUID],
) -> list[User]:
    result = await mo.get_person(
        person_uuid,
        [root_org_unit] + external_roots,
        [*ad_itsystem_user_keys, fk_itsystem_user_key],
        employee_email_user_key,
        mit_id_user_key,
        datetime.now(),
        sync_association_types,
    )

    if len(result.objects) == 0 or one(result.objects).current is None:
        raise WillNotSync("Not found. Strange.")

    mo_person = one(result.objects).current

    if mo_person is None:
        raise WillNotSync("Not found")

    # MitID UUIDs are unique per ituser. Map each mitid to its linked
    # ituser so we only assign nemloginUuid to that specific SAM account.
    # Unlinked or ambiguous mitids are dropped: the schema requires
    # nemloginUuid to be unique, and we have no way to know which ituser
    # a floating mitid belongs to.
    mit_id_by_ituser: dict[UUID, UUID] = {}
    for addr in mo_person.mitid:
        for linked in addr.ituser:
            mit_id_by_ituser[linked.uuid] = UUID(addr.value)

    if prefer_nickname and mo_person.nickname:
        name = Name(mo_person.nickname)
    else:
        name = Name(mo_person.name)

    # Tillidsfunktioner are the person's associations, resolved to org units
    # within the sync tree the same way as engagements. They are not tied to
    # an AD account in MO, so every user of the person carries all of them.
    functions: list[tuple[UUID, UUID]] = []
    if sync_functions:
        association_units = [
            (assoc, one(select_relevant(assoc.org_unit)))
            for assoc in select_relevant(mo_person.associations)
            if assoc.org_unit and assoc.association_type is not None
        ]
        functions = [
            (org_unit.uuid, assoc.association_type.uuid)
            for assoc, org_unit in association_units
            if not is_org_unit_excluded(
                org_unit, exclude_org_unit_level, exclude_org_units
            )
        ]

    users = []
    itusers, samaccounts = resolve_samaccounts(
        mo_person.itusers, ad_itsystem_user_keys, fk_itsystem_user_key
    )

    if not itusers:
        # Do not sync users without an AD account
        raise WillNotSync("No SAM Account")

    relevant_itusers = select_relevant(itusers)

    # Emails are matched to accounts via their ituser link. An email linked
    # to no account is a fallback for accounts without one of their own.
    unlinked = select_preferred(
        [email for email in mo_person.email if not email.ituser]
    )
    unlinked_email = unlinked.value if unlinked else None

    for ituser in relevant_itusers:
        extUuid = samaccounts.get(ituser.user_key)
        if extUuid is None:
            continue

        linked_email = select_preferred(ituser.addresses)
        email = linked_email.value if linked_email else unlinked_email

        # Include engagements valid now or in the future (Nutid/Fremtid).
        # The query returns all engagement validities, so pick the relevant
        # validity per engagement (current, else earliest future), and resolve
        # each to its org unit within the sync tree.
        engagement_validities = [
            validity for eng in ituser.engagements or [] for validity in eng.validities
        ]
        engagement_units = [
            (eng, one(select_relevant(eng.org_unit)))
            for eng in select_relevant(engagement_validities)
            # Skip engagements whose org unit is outside the sync root (the
            # query's ancestor filter returns an empty list for those).
            if eng.org_unit
        ]
        # Never create a position in an org unit we don't sync.
        positions = [
            Position(
                name=eng.job_function.name,
                orgUnitUuid=org_unit.uuid,
                titleUuid=eng.job_function.uuid if sync_titles else None,
            )
            for eng, org_unit in engagement_units
            if not is_org_unit_excluded(
                org_unit, exclude_org_unit_level, exclude_org_units
            )
        ]

        # Drop itusers whose in-tree engagements all resolved to excluded org
        # units. An ituser with no in-tree engagements at all is still synced
        # (see #70811).
        if engagement_units and not positions:
            continue

        users.append(
            User(
                person=mo_person.uuid,
                extUuid=extUuid,
                nemloginUuid=mit_id_by_ituser.get(ituser.uuid),
                userId=ituser.user_key,
                name=name,
                email=email,
                itsystem_user_key=ituser.itsystem.user_key,
                positions=positions,
                functions=[
                    UserFunction(
                        orgUnitUuid=org_unit_uuid,
                        functionUuid=function_uuid,
                    )
                    for org_unit_uuid, function_uuid in functions
                ],
            )
        )
    return users


async def fetch_users_from_db(session: depends.Session, uuid: UUID) -> list[User]:
    stmt = (
        select(User)
        .options(selectinload(User.positions), selectinload(User.functions))
        .where(User.person == uuid)
    )
    scalar_result = await session.scalars(stmt)
    users = scalar_result.all()

    return [user for user in users]


def _person_lock_key(person_uuid: UUID) -> int:
    # Stable signed 64-bit int derived from the UUID for use as the key
    # of pg_advisory_xact_lock(bigint). Keeps concurrent sync_person
    # calls for the same person serialized while letting different
    # persons proceed in parallel.
    digest = hashlib.blake2b(person_uuid.bytes, digest_size=8).digest()
    return int.from_bytes(digest, byteorder="big", signed=True)


async def sync_person(
    mo: depends.GraphQLClient,
    periodic_sync: depends.PeriodicSync,
    session: depends.Session,
    ad_itsystem_user_keys: list[str],
    fk_itsystem_user_key: str,
    employee_email_user_key: str,
    mit_id_user_key: str,
    root_org_unit: UUID,
    person_uuid: UUID,
    prefer_nickname: bool,
    sync_titles: bool,
    sync_functions: bool,
    sync_association_types: list[UUID] | None,
    external_roots: list[UUID],
    exclude_org_unit_level: UUID | None,
    exclude_org_units: list[UUID],
) -> None:
    await session.execute(
        text("SELECT pg_advisory_xact_lock(:k)"),
        {"k": _person_lock_key(person_uuid)},
    )
    try:
        users = await get_person(
            mo,
            ad_itsystem_user_keys,
            fk_itsystem_user_key,
            employee_email_user_key,
            mit_id_user_key,
            root_org_unit,
            person_uuid,
            prefer_nickname,
            sync_titles,
            sync_functions,
            sync_association_types,
            external_roots,
            exclude_org_unit_level,
            exclude_org_units,
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

    # Flush deletes before inserts so a reused unique nemloginUuid
    # (e.g. the AD account's FK partner changed → new extUuid, same
    # mitid) doesn't trip the constraint when SQLAlchemy's default
    # unit-of-work order issues INSERTs before DELETEs.
    if to_remove:
        await session.flush()

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
