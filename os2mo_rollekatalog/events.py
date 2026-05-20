# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0

from uuid import UUID

import structlog
from fastapi import APIRouter
from fastapi.encoders import jsonable_encoder
from fastramqpi.events import Event

from os2mo_rollekatalog import depends
from os2mo_rollekatalog import rollekatalog
from os2mo_rollekatalog.junkyard import flatten_validities
from os2mo_rollekatalog.orgunit import sync_org_unit
from os2mo_rollekatalog.person import sync_person
from os2mo_rollekatalog.titles import get_job_titles


router = APIRouter()
logger = structlog.stdlib.get_logger(__name__)


@router.post("/class")
async def handle_class(
    settings: depends.Settings,
    title_client: depends.TitleClient,
    mo: depends.GraphQLClient,
    event: Event[UUID],
) -> None:
    # If this function is changed to not being on demand, it won't work unless the mutation is changed.
    # Right now the mutation has `limit: 1`, so sync_job_titles is only triggered once
    if not settings.sync_titles:
        return
    titles = await get_job_titles(mo)
    payload = jsonable_encoder([title.to_rollekatalog_payload() for title in titles])
    logger.info("Uploading titles to Rollekatalog", payload=payload)
    await rollekatalog.upload(
        title_client,
        "/api/title",
        payload,
    )


@router.post("/person")
async def handle_person(
    settings: depends.Settings,
    mo: depends.GraphQLClient,
    ldap_client: depends.LDAPClient,
    periodic_sync: depends.PeriodicSync,
    session: depends.Session,
    event: Event[UUID],
) -> None:
    await sync_person(
        mo,
        ldap_client,
        periodic_sync,
        session,
        settings.ad_itsystem_user_key,
        settings.fk_itsystem_user_key,
        settings.employee_email_user_key,
        settings.mit_id_user_key,
        settings.root_org_unit,
        event.subject,
        settings.prefer_nickname,
        settings.sync_titles,
        settings.external_roots,
    )


@router.post("/ituser")
async def handle_ituser(
    settings: depends.Settings,
    mo: depends.GraphQLClient,
    ldap_client: depends.LDAPClient,
    periodic_sync: depends.PeriodicSync,
    session: depends.Session,
    event: Event[UUID],
) -> None:
    result = await mo.get_uuids_for_it_user(event.subject)
    for person_container in flatten_validities(result):
        if person_container.person is None:
            continue
        for person in person_container.person:
            await sync_person(
                mo,
                ldap_client,
                periodic_sync,
                session,
                settings.ad_itsystem_user_key,
                settings.fk_itsystem_user_key,
                settings.employee_email_user_key,
                settings.mit_id_user_key,
                settings.root_org_unit,
                person.uuid,
                settings.prefer_nickname,
                settings.sync_titles,
                settings.external_roots,
            )
            for engagement in person.engagements:
                await sync_org_unit(
                    mo,
                    ldap_client,
                    periodic_sync,
                    session,
                    settings.ad_itsystem_user_key,
                    settings.fk_itsystem_user_key,
                    settings.root_org_unit,
                    settings.exclude_org_unit_level,
                    engagement.org_unit_uuid,
                    settings.external_roots,
                )


@router.post("/address")
async def handle_address(
    settings: depends.Settings,
    mo: depends.GraphQLClient,
    ldap_client: depends.LDAPClient,
    periodic_sync: depends.PeriodicSync,
    session: depends.Session,
    event: Event[UUID],
) -> None:
    result = await mo.get_person_uuid_for_address(event.subject)
    for address in flatten_validities(result):
        if address.employee_uuid:
            await sync_person(
                mo,
                ldap_client,
                periodic_sync,
                session,
                settings.ad_itsystem_user_key,
                settings.fk_itsystem_user_key,
                settings.employee_email_user_key,
                settings.mit_id_user_key,
                settings.root_org_unit,
                address.employee_uuid,
                settings.prefer_nickname,
                settings.sync_titles,
                settings.external_roots,
            )


@router.post("/engagement")
async def handle_engagement(
    settings: depends.Settings,
    mo: depends.GraphQLClient,
    ldap_client: depends.LDAPClient,
    periodic_sync: depends.PeriodicSync,
    session: depends.Session,
    event: Event[UUID],
) -> None:
    result = await mo.get_person_uuid_for_engagement(event.subject)
    for engagement in flatten_validities(result):
        await sync_person(
            mo,
            ldap_client,
            periodic_sync,
            session,
            settings.ad_itsystem_user_key,
            settings.fk_itsystem_user_key,
            settings.employee_email_user_key,
            settings.mit_id_user_key,
            settings.root_org_unit,
            engagement.employee_uuid,
            settings.prefer_nickname,
            settings.sync_titles,
            settings.external_roots,
        )


@router.post("/org_unit")
async def handle_org_unit(
    settings: depends.Settings,
    mo: depends.GraphQLClient,
    ldap_client: depends.LDAPClient,
    periodic_sync: depends.PeriodicSync,
    session: depends.Session,
    event: Event[UUID],
) -> None:
    await sync_org_unit(
        mo,
        ldap_client,
        periodic_sync,
        session,
        settings.ad_itsystem_user_key,
        settings.fk_itsystem_user_key,
        settings.root_org_unit,
        settings.exclude_org_unit_level,
        event.subject,
        settings.external_roots,
    )


@router.post("/kle")
async def handle_kle(
    settings: depends.Settings,
    mo: depends.GraphQLClient,
    ldap_client: depends.LDAPClient,
    periodic_sync: depends.PeriodicSync,
    session: depends.Session,
    event: Event[UUID],
) -> None:
    result = await mo.get_org_unit_uuid_for_kle(event.subject)
    for kle in flatten_validities(result):
        await sync_org_unit(
            mo,
            ldap_client,
            periodic_sync,
            session,
            settings.ad_itsystem_user_key,
            settings.fk_itsystem_user_key,
            settings.root_org_unit,
            settings.exclude_org_unit_level,
            kle.org_unit_uuid,
            settings.external_roots,
        )


@router.post("/manager")
async def handle_manager(
    settings: depends.Settings,
    mo: depends.GraphQLClient,
    ldap_client: depends.LDAPClient,
    periodic_sync: depends.PeriodicSync,
    session: depends.Session,
    event: Event[UUID],
) -> None:
    result = await mo.get_org_unit_uuid_for_manager(event.subject)
    for manager in flatten_validities(result):
        await sync_org_unit(
            mo,
            ldap_client,
            periodic_sync,
            session,
            settings.ad_itsystem_user_key,
            settings.fk_itsystem_user_key,
            settings.root_org_unit,
            settings.exclude_org_unit_level,
            manager.org_unit_uuid,
            settings.external_roots,
        )
