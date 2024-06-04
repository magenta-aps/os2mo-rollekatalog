# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from datetime import datetime
from uuid import UUID

from os2mo_rollekatalog import depends
from os2mo_rollekatalog.models import Name
from os2mo_rollekatalog.models import Position
from os2mo_rollekatalog.models import SamAccountName
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
        email = [
            addr.value for obj in result.addresses.objects for addr in obj.validities
        ][-1]
    except IndexError:
        email = None

    if use_nickname:
        name = Name(mo_person.nickname)
    else:
        name = Name(mo_person.name)

    try:
        sam_account_name = SamAccountName(
            [it.user_key for obj in result.itusers.objects for it in obj.validities][-1]
        )
    except IndexError:
        # Do not sync users without an AD account
        return None

    engagements = [eng for obj in result.engagements.objects for eng in obj.validities]
    positions = [
        Position(
            name=engagement.job_function.name,
            orgUnitUuid=engagement.org_unit_uuid,
            titleUuid=engagement.job_function.uuid if sync_titles else None,
        )
        for engagement in engagements
    ]

    return User(
        extUuid=mo_person.uuid,
        userId=sam_account_name,
        name=name,
        email=email,
        positions=positions,
    )
