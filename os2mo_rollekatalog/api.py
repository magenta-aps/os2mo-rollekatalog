# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
import structlog
from fastapi import APIRouter
from uuid import UUID

from os2mo_rollekatalog import depends
from os2mo_rollekatalog.models import User
from os2mo_rollekatalog.models import OrgUnit
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
async def titles(settings: depends.Settings, mo: depends.GraphQLClient) -> list[Title]:
    """Get job titles that will be synced."""
    return await get_job_titles(mo, settings.sync_titles)


@router.get("/person")
async def person(
    settings: depends.Settings, mo: depends.GraphQLClient, person_uuid: UUID
) -> User | None:
    """See how a person will be synced."""
    return await get_person(
        mo,
        settings.itsystem_user_key,
        settings.root_org_unit,
        person_uuid,
        settings.use_nickname,
        settings.sync_titles,
    )


@router.get("/org_unit")
async def org_unit(
    settings: depends.Settings, mo: depends.GraphQLClient, uuid: UUID
) -> OrgUnit | None:
    """See how an org unit will be synced."""
    return await get_org_unit(
        mo,
        settings.itsystem_user_key,
        settings.root_org_unit,
        uuid,
    )


@router.get("/dump_user_cache")
async def dump_user_cache(user_cache: depends.UserCache) -> dict[UUID, User]:
    """Dump the user cache."""
    return user_cache


@router.get("/dump_org_unit_cache")
async def dump_org_unit_cache(
    org_unit_cache: depends.OrgUnitCache,
) -> dict[UUID, OrgUnit]:
    """Dump the org unit cache."""
    return org_unit_cache
