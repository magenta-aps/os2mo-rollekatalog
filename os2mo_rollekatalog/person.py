# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from datetime import datetime
from uuid import UUID

from os2mo_rollekatalog import depends
from os2mo_rollekatalog.junkyard import NoSuitableSamAccount
from os2mo_rollekatalog.junkyard import flatten_validities
from os2mo_rollekatalog.junkyard import in_org_tree
from os2mo_rollekatalog.junkyard import pick_samaccount
from os2mo_rollekatalog.models import Name
from os2mo_rollekatalog.models import Position
from os2mo_rollekatalog.models import User
from os2mo_rollekatalog.models import UserCache


async def get_person(
    mo: depends.GraphQLClient,
    itsystem_user_key: str,
    root_org_unit: UUID,
    person_uuid: UUID,
    use_nickname: bool,
    sync_titles: bool,
) -> User | None:
    result = await mo.get_person(itsystem_user_key, datetime.now(), person_uuid)

    if (
        len(result.employees.objects) == 0
        or result.employees.objects[0].current is None
    ):
        return None

    mo_person = result.employees.objects[0].current

    try:
        # Behaviour of the old integration 🤷
        email = list(flatten_validities(result.addresses))[-1].value
    except IndexError:
        email = None

    if use_nickname:
        name = Name(mo_person.nickname)
    else:
        name = Name(mo_person.name)

    try:
        sam_account_name = pick_samaccount(list(flatten_validities(result.itusers)))
    except NoSuitableSamAccount:
        # Do not sync users without an AD account
        return None

    positions = []
    for engagement in flatten_validities(result.engagements):
        for org_unit in engagement.org_unit:
            if not in_org_tree(root_org_unit, org_unit):
                continue
            positions.append(
                Position(
                    name=engagement.job_function.name,
                    orgUnitUuid=org_unit.uuid,
                    titleUuid=engagement.job_function.uuid if sync_titles else None,
                )
            )

    return User(
        extUuid=mo_person.uuid,
        userId=sam_account_name,
        name=name,
        email=email,
        positions=positions,
    )


async def sync_person(
    mo: depends.GraphQLClient,
    rollekatalog: depends.Rollekatalog,
    cache: UserCache,
    itsystem_user_key: str,
    root_org_unit: UUID,
    person_uuid: UUID,
    use_nickname: bool,
    sync_titles: bool,
) -> None:
    user = await get_person(
        mo, itsystem_user_key, root_org_unit, person_uuid, use_nickname, sync_titles
    )
    if user is None:
        if person_uuid in cache:
            del cache[person_uuid]
            rollekatalog.sync_soon()
    else:
        if user == cache.get(person_uuid):
            return
        cache[person_uuid] = user
        rollekatalog.sync_soon()
