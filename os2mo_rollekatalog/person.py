# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from datetime import datetime
from uuid import UUID

from os2mo_rollekatalog import depends
from os2mo_rollekatalog.junkyard import NoSuitableSamAccount
from os2mo_rollekatalog.junkyard import flatten_validities
from os2mo_rollekatalog.junkyard import pick_samaccount
from os2mo_rollekatalog.models import Name
from os2mo_rollekatalog.models import Position
from os2mo_rollekatalog.models import User


async def get_person(
    mo: depends.GraphQLClient,
    itsystem_user_key: str,
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

    positions = [
        Position(
            name=engagement.job_function.name,
            orgUnitUuid=engagement.org_unit_uuid,
            titleUuid=engagement.job_function.uuid if sync_titles else None,
        )
        for engagement in flatten_validities(result.engagements)
    ]

    return User(
        extUuid=mo_person.uuid,
        userId=sam_account_name,
        name=name,
        email=email,
        positions=positions,
    )


async def sync_person(
    mo: depends.GraphQLClient,
    cache: dict[UUID, User],
    itsystem_user_key: str,
    person_uuid: UUID,
    use_nickname: bool,
    sync_titles: bool,
) -> None:
    user = await get_person(
        mo, itsystem_user_key, person_uuid, use_nickname, sync_titles
    )
    if user is None:
        return
    cache[person_uuid] = user
