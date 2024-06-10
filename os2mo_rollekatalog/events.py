# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from datetime import datetime

import structlog
from fastramqpi.ramqp.mo import MORouter
from fastramqpi.ramqp.mo import PayloadUUID

from os2mo_rollekatalog import depends
from os2mo_rollekatalog.person import sync_person
from os2mo_rollekatalog.titles import get_job_titles

router = MORouter()
logger = structlog.get_logger(__name__)


@router.register("class")
async def handler(mo: depends.GraphQLClient) -> None:
    version = await mo.get_version()
    print(version)


@router.register("class")
async def sync_job_titles(mo: depends.GraphQLClient) -> None:
    titles = await get_job_titles(mo)
    print(f"found the following titles {titles}")
    # TODO send to rollekatalog https://htk.rollekatalog.dk/download/api.html#_update_all_titles


@router.register("person")
async def handle_person(
    person_uuid: PayloadUUID,
    settings: depends.Settings,
    mo: depends.GraphQLClient,
    user_cache: depends.UserCache,
) -> None:
    await sync_person(
        mo,
        user_cache,
        settings.itsystem_user_key,
        person_uuid,
        settings.use_nickname,
        settings.sync_titles,
    )


@router.register("ituser")
async def handle_ituser(
    ituser_uuid: PayloadUUID,
    settings: depends.Settings,
    mo: depends.GraphQLClient,
    user_cache: depends.UserCache,
) -> None:
    result = await mo.get_person_uuid_for_it_user(datetime.now(), ituser_uuid)
    uuids = {
        val.employee_uuid
        for obj in result.objects
        for val in obj.validities
        if val.employee_uuid is not None
    }
    for person_uuid in uuids:
        await sync_person(
            mo,
            user_cache,
            settings.itsystem_user_key,
            person_uuid,
            settings.use_nickname,
            settings.sync_titles,
        )


@router.register("address")
async def handle_address(
    address_uuid: PayloadUUID,
    settings: depends.Settings,
    mo: depends.GraphQLClient,
    user_cache: depends.UserCache,
) -> None:
    result = await mo.get_person_uuid_for_address(datetime.now(), address_uuid)
    uuids = {
        val.employee_uuid
        for obj in result.objects
        for val in obj.validities
        if val.employee_uuid is not None
    }
    for person_uuid in uuids:
        await sync_person(
            mo,
            user_cache,
            settings.itsystem_user_key,
            person_uuid,
            settings.use_nickname,
            settings.sync_titles,
        )


@router.register("engagement")
async def handle_engagement(
    engagement_uuid: PayloadUUID,
    settings: depends.Settings,
    mo: depends.GraphQLClient,
    user_cache: depends.UserCache,
) -> None:
    result = await mo.get_person_uuid_for_engagement(datetime.now(), engagement_uuid)
    uuids = {
        val.employee_uuid
        for obj in result.objects
        for val in obj.validities
        if val.employee_uuid is not None
    }
    for person_uuid in uuids:
        await sync_person(
            mo,
            user_cache,
            settings.itsystem_user_key,
            person_uuid,
            settings.use_nickname,
            settings.sync_titles,
        )
