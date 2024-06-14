# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from datetime import datetime

import structlog
from fastapi.encoders import jsonable_encoder
from fastramqpi.ramqp.mo import MORouter
from fastramqpi.ramqp.mo import PayloadUUID

from os2mo_rollekatalog import depends
from os2mo_rollekatalog import rollekatalog
from os2mo_rollekatalog.junkyard import flatten_validities
from os2mo_rollekatalog.orgunit import sync_org_unit
from os2mo_rollekatalog.person import sync_person
from os2mo_rollekatalog.titles import get_job_titles


router = MORouter()
logger = structlog.get_logger(__name__)


@router.register("class")
async def handler(mo: depends.GraphQLClient) -> None:
    version = await mo.get_version()
    print(version)


@router.register("class")
async def sync_job_titles(
    settings: depends.Settings,
    title_client: depends.TitleClient,
    mo: depends.GraphQLClient,
) -> None:
    if not settings.sync_titles:
        return
    titles = await get_job_titles(mo)
    payload = jsonable_encoder({"titles": [title.dict() for title in titles]})
    logger.info("Uploading titles to Rollekatalog", payload=payload)
    await rollekatalog.upload(
        title_client,
        f"{settings.rollekatalog_url}/api/title",
        settings.api_key,
        payload,
    )


@router.register("person")
async def handle_person(
    person_uuid: PayloadUUID,
    settings: depends.Settings,
    mo: depends.GraphQLClient,
    rollekatalog: depends.Rollekatalog,
    user_cache: depends.UserCache,
) -> None:
    await sync_person(
        mo,
        rollekatalog,
        user_cache,
        settings.itsystem_user_key,
        settings.root_org_unit,
        person_uuid,
        settings.use_nickname,
        settings.sync_titles,
    )


@router.register("ituser")
async def handle_ituser(
    ituser_uuid: PayloadUUID,
    settings: depends.Settings,
    mo: depends.GraphQLClient,
    rollekatalog: depends.Rollekatalog,
    user_cache: depends.UserCache,
    org_unit_cache: depends.OrgUnitCache,
) -> None:
    result = await mo.get_uuids_for_it_user(ituser_uuid)
    for person_container in flatten_validities(result):
        if person_container.person is None:
            continue
        for person in person_container.person:
            await sync_person(
                mo,
                rollekatalog,
                user_cache,
                settings.itsystem_user_key,
                settings.root_org_unit,
                person.uuid,
                settings.use_nickname,
                settings.sync_titles,
            )
            for engagement in person.engagements:
                await sync_org_unit(
                    mo,
                    rollekatalog,
                    org_unit_cache,
                    user_cache,
                    settings.itsystem_user_key,
                    settings.root_org_unit,
                    engagement.org_unit_uuid,
                )


@router.register("address")
async def handle_address(
    address_uuid: PayloadUUID,
    settings: depends.Settings,
    mo: depends.GraphQLClient,
    rollekatalog: depends.Rollekatalog,
    user_cache: depends.UserCache,
) -> None:
    result = await mo.get_person_uuid_for_address(datetime.now(), address_uuid)
    for address in flatten_validities(result):
        if address.employee_uuid:
            await sync_person(
                mo,
                rollekatalog,
                user_cache,
                settings.itsystem_user_key,
                settings.root_org_unit,
                address.employee_uuid,
                settings.use_nickname,
                settings.sync_titles,
            )


@router.register("engagement")
async def handle_engagement(
    engagement_uuid: PayloadUUID,
    settings: depends.Settings,
    mo: depends.GraphQLClient,
    rollekatalog: depends.Rollekatalog,
    user_cache: depends.UserCache,
) -> None:
    result = await mo.get_person_uuid_for_engagement(datetime.now(), engagement_uuid)
    for engagement in flatten_validities(result):
        await sync_person(
            mo,
            rollekatalog,
            user_cache,
            settings.itsystem_user_key,
            settings.root_org_unit,
            engagement.employee_uuid,
            settings.use_nickname,
            settings.sync_titles,
        )


@router.register("org_unit")
async def handle_org_unit(
    org_unit_uuid: PayloadUUID,
    settings: depends.Settings,
    mo: depends.GraphQLClient,
    rollekatalog: depends.Rollekatalog,
    org_unit_cache: depends.OrgUnitCache,
    user_cache: depends.UserCache,
) -> None:
    await sync_org_unit(
        mo,
        rollekatalog,
        org_unit_cache,
        user_cache,
        settings.itsystem_user_key,
        settings.root_org_unit,
        org_unit_uuid,
    )


@router.register("kle")
async def handle_kle(
    kle_uuid: PayloadUUID,
    settings: depends.Settings,
    mo: depends.GraphQLClient,
    rollekatalog: depends.Rollekatalog,
    org_unit_cache: depends.OrgUnitCache,
    user_cache: depends.UserCache,
) -> None:
    result = await mo.get_org_unit_uuid_for_kle(datetime.now(), kle_uuid)
    for kle in flatten_validities(result):
        await sync_org_unit(
            mo,
            rollekatalog,
            org_unit_cache,
            user_cache,
            settings.itsystem_user_key,
            settings.root_org_unit,
            kle.org_unit_uuid,
        )


@router.register("manager")
async def handle_manager(
    manager_uuid: PayloadUUID,
    settings: depends.Settings,
    mo: depends.GraphQLClient,
    rollekatalog: depends.Rollekatalog,
    org_unit_cache: depends.OrgUnitCache,
    user_cache: depends.UserCache,
) -> None:
    result = await mo.get_org_unit_uuid_for_manager(datetime.now(), manager_uuid)
    for manager in flatten_validities(result):
        await sync_org_unit(
            mo,
            rollekatalog,
            org_unit_cache,
            user_cache,
            settings.itsystem_user_key,
            settings.root_org_unit,
            manager.org_unit_uuid,
        )
