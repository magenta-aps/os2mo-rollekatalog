# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from uuid import UUID

import structlog
from fastapi import APIRouter

from os2mo_rollekatalog import depends
from os2mo_rollekatalog.junkyard import WillNotSync
from os2mo_rollekatalog.models import Title
from os2mo_rollekatalog.person import fetch_person_from_db
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


@router.get("/debug/person/{uuid}")
async def person(
    settings: depends.Settings,
    mo: depends.GraphQLClient,
    ldap_client: depends.LDAPClient,
    uuid: UUID,
) -> dict:
    """See how a person will be synced, or debug why it is not to be."""
    try:
        person = await get_person(
            mo,
            ldap_client,
            settings.itsystem_user_key,
            settings.root_org_unit,
            uuid,
            settings.use_nickname,
            settings.sync_titles,
        )
    except WillNotSync as e:
        return {"error": e.message}
    return person.to_rollekatalog_payload()


@router.post("/sync/person/{uuid}")
async def sync_person_on_demand(
    settings: depends.Settings,
    mo: depends.GraphQLClient,
    ldap_client: depends.LDAPClient,
    rollekatalog: depends.Rollekatalog,
    session: depends.Session,
    uuid: UUID,
) -> None:
    """Sync person."""
    await sync_person(
        mo,
        ldap_client,
        rollekatalog,
        session,
        settings.itsystem_user_key,
        settings.root_org_unit,
        uuid,
        settings.use_nickname,
        settings.sync_titles,
    )


@router.get("/cache/person/{uuid}")
async def person_from_cache(session: depends.Session, uuid: UUID) -> dict | None:
    """Inspect a person from the cache."""
    user = await fetch_person_from_db(session, uuid)
    if user is None:
        return None
    return user.to_rollekatalog_payload()


@router.get("/debug/org_unit/{uuid}")
async def org_unit(
    settings: depends.Settings,
    mo: depends.GraphQLClient,
    ldap_client: depends.LDAPClient,
    uuid: UUID,
) -> dict:
    """See how an org unit will be synced, or debug why it is not to be."""
    try:
        org_unit = await get_org_unit(
            mo,
            ldap_client,
            settings.itsystem_user_key,
            settings.root_org_unit,
            uuid,
        )
    except WillNotSync as e:
        return {"error": e.message}
    return org_unit.to_rollekatalog_payload()


@router.post("/sync/org_unit/{uuid}")
async def sync_org_unit_on_demand(
    settings: depends.Settings,
    mo: depends.GraphQLClient,
    ldap_client: depends.LDAPClient,
    rollekatalog: depends.Rollekatalog,
    session: depends.Session,
    uuid: UUID,
) -> None:
    """Sync org unit."""
    await sync_org_unit(
        mo,
        ldap_client,
        rollekatalog,
        session,
        settings.itsystem_user_key,
        settings.root_org_unit,
        uuid,
    )


@router.get("/cache/org_unit/{uuid}")
async def org_unit_from_cache(session: depends.Session, uuid: UUID) -> dict | None:
    """Inspect an org unit from the cache."""
    org = await fetch_org_unit_from_db(session, uuid)
    if org is None:
        return None
    return org.to_rollekatalog_payload()
