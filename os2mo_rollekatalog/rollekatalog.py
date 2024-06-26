# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0

import asyncio
from contextlib import asynccontextmanager
from typing import Any
from typing import Never

import structlog
from fastramqpi.metrics import dipex_last_success_timestamp
from httpx import AsyncClient
from httpx import HTTPStatusError
from httpx import TimeoutException
from pydantic import HttpUrl
from pydantic import SecretStr
from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from os2mo_rollekatalog.models import OrgUnit
from os2mo_rollekatalog.models import User


logger = structlog.get_logger(__name__)


async def upload(
    client: AsyncClient, url: str, api_key: SecretStr, payload: Any
) -> None:
    r = await client.post(
        url, json=payload, headers={"ApiKey": api_key.get_secret_value()}
    )
    r.raise_for_status()


class Rollekatalog:
    """Periodically send data to OS2rollekatalog.

    This only writes to the Organisation API (org and users). Titles are synced
    immediately when an event arrives.

    Only sync to Rollekatalog if there are changes. When we notice a change, we
    wait *interval* seconds before we write to Rollekatalog. Changes made while
    we wait *interval* seconds are also synced.
    """

    def __init__(
        self,
        url: HttpUrl,
        api_key: SecretStr,
        interval: int,
        sessionmaker: async_sessionmaker[AsyncSession],
    ):
        self.url = url
        self.api_key = api_key
        self.interval = interval
        self.sessionmaker = sessionmaker
        self.event = asyncio.Event()
        self.client = AsyncClient()

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
                            select(User)
                            .options(selectinload(User.positions))
                            .join(User.positions)
                        )
                    )
                    .scalars()
                    .all()
                )
                org_units = [org.to_rollekatalog_payload() for org in org_units_from_db]
                users = [user.to_rollekatalog_payload() for user in users_from_db]

            if org_units == [] and users == []:
                logger.warning("No data to upload")
                self.sync_soon()
                continue

            payload = {"orgUnits": org_units, "users": users}
            logger.info("Uploading org units and users to Rollekatalog")
            try:
                await upload(
                    self.client,
                    f"{self.url}/api/organisation/v3",
                    self.api_key,
                    payload,
                )
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
