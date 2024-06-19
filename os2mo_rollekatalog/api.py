# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
import structlog
from fastapi import APIRouter
from uuid import UUID

from os2mo_rollekatalog import depends
from os2mo_rollekatalog.models import Title
from os2mo_rollekatalog.person import get_person
from os2mo_rollekatalog.orgunit import get_org_unit
from os2mo_rollekatalog.titles import get_job_titles


router = APIRouter()
logger = structlog.get_logger(__name__)


@router.get("/hello")
async def hello() -> str:
    """Greetings."""
    return "World!"


@router.get("/titles")
async def titles(mo: depends.GraphQLClient) -> list[Title]:
    """Get job titles that would be synced with SYNC_TITLES=true."""
    return await get_job_titles(mo)


@router.get("/person")
async def person(
    settings: depends.Settings, mo: depends.GraphQLClient, person_uuid: UUID
) -> dict | None:
    """See how a person will be synced."""
    person = await get_person(
        mo,
        settings.itsystem_user_key,
        settings.root_org_unit,
        person_uuid,
        settings.use_nickname,
        settings.sync_titles,
    )
    if person is None:
        return None
    return person.to_rollekatalog_payload()


@router.get("/org_unit")
async def org_unit(
    settings: depends.Settings, mo: depends.GraphQLClient, uuid: UUID
) -> dict | None:
    """See how an org unit will be synced."""
    org_unit = await get_org_unit(
        mo,
        settings.itsystem_user_key,
        settings.root_org_unit,
        uuid,
    )
    if org_unit is None:
        return None
    return org_unit.to_rollekatalog_payload()
