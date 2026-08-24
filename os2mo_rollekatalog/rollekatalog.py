# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0

import asyncio
from contextlib import asynccontextmanager
from typing import Any
from typing import Never
from typing import NewType

import structlog
from fastramqpi.metrics import dipex_last_success_timestamp
from httpx import AsyncClient
from httpx import HTTPStatusError
from httpx import MockTransport
from httpx import Request
from httpx import Response
from httpx import TimeoutException
from pydantic import AnyHttpUrl
from pydantic import SecretStr
from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from os2mo_rollekatalog.models import OrgUnit
from os2mo_rollekatalog.models import User


logger = structlog.stdlib.get_logger(__name__)


RollekatalogClient = NewType("RollekatalogClient", AsyncClient)


def create_authenticated_client(
    sync_enabled: bool, base_url: AnyHttpUrl, api_key: SecretStr, httpx_timeout: int
) -> RollekatalogClient:
    if sync_enabled:
        client = AsyncClient(
            base_url=base_url,
            headers={"ApiKey": api_key.get_secret_value()},
            timeout=httpx_timeout,
        )
    else:

        def handler(request: Request) -> Response:
            logger.info("Sync to Rollekatalog is disabled. Not syncing.")
            return Response(200, json=[])

        client = AsyncClient(base_url=base_url, transport=MockTransport(handler))
    return RollekatalogClient(client)


async def upload(
    client: RollekatalogClient,
    path: str,
    payload: Any,
    params: dict[str, str] | None = None,
) -> None:
    try:
        r = await client.post(path, json=payload, params=params)
        r.raise_for_status()
    except HTTPStatusError as e:
        logger.error("Error: Failed to upload data", http_body=e.response.text)
        raise e


class PeriodicSync:
    """Periodically send data to OS2rollekatalog.

    This only writes to the Organisation API (org and users). Titles are synced
    immediately when an event arrives.

    Only sync to Rollekatalog if there are changes. When we notice a change, we
    wait *interval* seconds before we write to Rollekatalog. Changes made while
    we wait *interval* seconds are also synced.
    """

    def __init__(
        self,
        interval: int,
        client: RollekatalogClient,
        sessionmaker: async_sessionmaker[AsyncSession],
        itsystem_domains: dict[str, str],
    ):
        self.interval = interval
        self.sessionmaker = sessionmaker
        self.event = asyncio.Event()
        self.client = client
        self.itsystem_domains = itsystem_domains

    def sync_soon(self) -> None:
        self.event.set()

    async def _background(self) -> Never:
        while True:
            await self.event.wait()
            self.event.clear()
            await asyncio.sleep(self.interval)

            async with self.sessionmaker() as session, session.begin():
                org_units_from_db = (
                    (
                        await session.execute(
                            select(OrgUnit).options(selectinload(OrgUnit.manager))
                        )
                    )
                    .scalars()
                    .all()
                )
                users_from_db = (
                    (
                        await session.execute(
                            select(User).options(
                                selectinload(User.positions),
                                selectinload(User.functions),
                            )
                        )
                    )
                    .scalars()
                    .all()
                )
                org_units = [org.to_rollekatalog_payload() for org in org_units_from_db]
                # One upload per Rollekatalog domain; None is the primary
                # domain. Its call carries the org units and comes first, so
                # org units exist before other domains' users reference them.
                # Rollekatalog compares users per domain, so every domain is
                # synced on every run — also when it has no users left.
                users_by_domain: dict[str | None, list] = {
                    domain: [] for domain in [None, *self.itsystem_domains.values()]
                }
                for user in users_from_db:
                    domain = (
                        self.itsystem_domains.get(user.itsystem_user_key)
                        if user.itsystem_user_key
                        else None
                    )
                    users_by_domain[domain].append(user.to_rollekatalog_payload())

            if org_units == [] and not any(users_by_domain.values()):
                logger.warning("No data to upload")
                self.sync_soon()
                continue

            try:
                for domain, users in users_by_domain.items():
                    # Org units are included in every call: Rollekatalog only
                    # imports them from the primary domain's call, but
                    # validates user positions against them in all calls.
                    payload = {"orgUnits": org_units, "users": users}
                    params = None if domain is None else {"domain": domain}
                    logger.info(
                        "Uploading to Rollekatalog",
                        domain=domain,
                        users=len(users),
                    )
                    await upload(
                        self.client,
                        "/api/organisation/v3",
                        payload,
                        params=params,
                    )
                logger.info("Upload successful")
                dipex_last_success_timestamp.set_to_current_time()
            except HTTPStatusError as e:
                logger.warning("Failed to upload organisation", exception=str(e))
                self.sync_soon()
            except TimeoutException as e:
                logger.warning("Request timed out", exception=str(e))
                self.sync_soon()
            except Exception as e:
                logger.warning("Unknown exception", exception=str(e))
                self.sync_soon()

    def start(self) -> None:
        # Keep a reference to avoid garbage collection
        self._task = asyncio.create_task(self._background())

    @asynccontextmanager
    async def lifespan(self):
        self.start()
        yield
        await self.client.aclose()
