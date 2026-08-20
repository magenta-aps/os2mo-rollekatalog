# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from uuid import UUID

import structlog
from fastapi import APIRouter
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload

from os2mo_rollekatalog import depends
from os2mo_rollekatalog.functions import fetch_function_map
from os2mo_rollekatalog.functions import get_function_types
from os2mo_rollekatalog.junkyard import WillNotSync
from os2mo_rollekatalog.models import Function
from os2mo_rollekatalog.models import Title
from os2mo_rollekatalog.models import User
from os2mo_rollekatalog.models import OrgUnit
from os2mo_rollekatalog.person import fetch_users_from_db
from os2mo_rollekatalog.person import get_person
from os2mo_rollekatalog.person import sync_person
from os2mo_rollekatalog.orgunit import fetch_org_unit_from_db
from os2mo_rollekatalog.orgunit import get_org_unit
from os2mo_rollekatalog.orgunit import sync_org_unit
from os2mo_rollekatalog.titles import get_job_titles


router = APIRouter()
logger = structlog.stdlib.get_logger(__name__)


@router.get("/titles")
async def titles(mo: depends.GraphQLClient) -> list[Title]:
    """Get job titles that would be synced with SYNC_TITLES=true."""
    return await get_job_titles(mo)


@router.get("/functions")
async def functions(mo: depends.GraphQLClient) -> dict[UUID, str]:
    """Get association types that would be synced with SYNC_FUNCTIONS=true."""
    return await get_function_types(mo)


@router.get("/cache/functions")
async def functions_from_cache(session: depends.Session) -> list[dict]:
    """Inspect the function catalog and its Rollekatalog UUID mapping."""
    functions = (await session.scalars(select(Function))).all()
    return [
        {"mo_uuid": f.mo_uuid, "rk_uuid": f.rk_uuid, "name": f.name} for f in functions
    ]


@router.get("/cache/stikprøve/person")
async def random_users(session: depends.Session, count: int = 5) -> list:
    """
    Get a random sample of users from the cache.
    """
    stmt = (
        select(User)
        .options(selectinload(User.positions), selectinload(User.functions))
        .order_by(func.random())
        .limit(count)
    )

    scalar_result = await session.scalars(stmt)
    users = scalar_result.all()

    function_uuids = await fetch_function_map(session)
    return [user.to_rollekatalog_payload(function_uuids) for user in users]


@router.get("/cache/stikprøve/org_unit")
async def random_org_units(session: depends.Session, count: int = 5) -> list:
    """
    Get a random sample of org units from the cache.
    """
    stmt = (
        select(OrgUnit)
        .options(selectinload(OrgUnit.manager))  # only relationship
        .order_by(func.random())
        .limit(count)
    )

    scalar_result = await session.scalars(stmt)
    orgunits = scalar_result.all()

    return [ou.to_rollekatalog_payload() for ou in orgunits]


@router.get("/debug/person/{uuid}")
async def person(
    settings: depends.Settings,
    mo: depends.GraphQLClient,
    session: depends.Session,
    uuid: UUID,
) -> list | dict:
    """See how a person will be synced, or debug why it is not to be."""
    try:
        users = await get_person(
            mo,
            settings.ad_itsystem_user_keys,
            settings.fk_itsystem_user_key,
            settings.employee_email_user_key,
            settings.mit_id_user_key,
            settings.root_org_unit,
            uuid,
            settings.prefer_nickname,
            settings.sync_titles,
            settings.sync_functions,
            settings.external_roots,
            settings.exclude_org_unit_level,
            settings.exclude_org_units,
        )
    except WillNotSync as e:
        return {"error": e.message}
    function_uuids = await fetch_function_map(session)
    return [u.to_rollekatalog_payload(function_uuids) for u in users]


@router.post("/sync/person/{uuid}")
async def sync_person_on_demand(
    settings: depends.Settings,
    mo: depends.GraphQLClient,
    periodic_sync: depends.PeriodicSync,
    session: depends.Session,
    uuid: UUID,
) -> None:
    """Sync person."""
    await sync_person(
        mo,
        periodic_sync,
        session,
        settings.ad_itsystem_user_keys,
        settings.fk_itsystem_user_key,
        settings.employee_email_user_key,
        settings.mit_id_user_key,
        settings.root_org_unit,
        uuid,
        settings.prefer_nickname,
        settings.sync_titles,
        settings.sync_functions,
        settings.external_roots,
        settings.exclude_org_unit_level,
        settings.exclude_org_units,
    )


@router.get("/cache/person/{uuid}")
async def person_from_cache(session: depends.Session, uuid: UUID) -> list:
    """Inspect a person from the cache."""
    users = await fetch_users_from_db(session, uuid)
    function_uuids = await fetch_function_map(session)
    return [u.to_rollekatalog_payload(function_uuids) for u in users]


@router.get("/debug/org_unit/{uuid}")
async def org_unit(
    settings: depends.Settings,
    mo: depends.GraphQLClient,
    uuid: UUID,
) -> dict:
    """See how an org unit will be synced, or debug why it is not to be."""
    try:
        org_unit = await get_org_unit(
            mo,
            settings.ad_itsystem_user_keys,
            settings.fk_itsystem_user_key,
            settings.manager_itsystem_user_key,
            settings.root_org_unit,
            settings.exclude_org_unit_level,
            settings.exclude_org_units,
            uuid,
            settings.external_roots,
        )
    except WillNotSync as e:
        return {"error": e.message}
    return org_unit.to_rollekatalog_payload()


@router.post("/sync/org_unit/{uuid}")
async def sync_org_unit_on_demand(
    settings: depends.Settings,
    mo: depends.GraphQLClient,
    periodic_sync: depends.PeriodicSync,
    session: depends.Session,
    uuid: UUID,
) -> None:
    """Sync org unit."""
    await sync_org_unit(
        mo,
        periodic_sync,
        session,
        settings.ad_itsystem_user_keys,
        settings.fk_itsystem_user_key,
        settings.manager_itsystem_user_key,
        settings.root_org_unit,
        settings.exclude_org_unit_level,
        settings.exclude_org_units,
        uuid,
        settings.external_roots,
    )


@router.get("/cache/org_unit/{uuid}")
async def org_unit_from_cache(session: depends.Session, uuid: UUID) -> dict | None:
    """Inspect an org unit from the cache."""
    org = await fetch_org_unit_from_db(session, uuid)
    if org is None:
        return None
    return org.to_rollekatalog_payload()


@router.post("/trigger/all")
async def trigger_refresh_all(settings: depends.Settings, mo: depends.GraphQLClient):
    await mo.refresh_all(
        None if settings.external_roots else [settings.root_org_unit],
    )
