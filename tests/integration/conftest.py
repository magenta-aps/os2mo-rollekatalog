# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from collections.abc import AsyncIterator
from uuid import uuid4
from uuid import UUID

import pytest
from asgi_lifespan import LifespanManager
from asgi_lifespan._types import ASGIApp
from fastapi import FastAPI
from gql.client import AsyncClientSession
from httpx import AsyncClient
from httpx import ASGITransport
from pytest import MonkeyPatch

from os2mo_rollekatalog.app import create_app


@pytest.fixture
def root_uuid():
    return uuid4()


@pytest.fixture
async def _app(monkeypatch: MonkeyPatch, root_uuid: UUID) -> FastAPI:
    monkeypatch.setenv("ROLLEKATALOG_URL", "http://example.org")
    monkeypatch.setenv("API_KEY", "dummy")
    monkeypatch.setenv("ROOT_ORG_UNIT", str(root_uuid))
    monkeypatch.setenv("ITSYSTEM_USER_KEY", "Active Directory")

    app = create_app()
    return app


@pytest.fixture
async def asgiapp(_app: FastAPI) -> AsyncIterator[ASGIApp]:
    """ASGI app with lifespan run."""
    async with LifespanManager(_app) as manager:
        yield manager.app


@pytest.fixture
async def app(_app: FastAPI, asgiapp: ASGIApp) -> FastAPI:
    """FastAPI app with lifespan run."""
    return _app


@pytest.fixture
async def test_client(asgiapp: ASGIApp) -> AsyncIterator[AsyncClient]:
    """Create test client with associated lifecycles."""
    transport = ASGITransport(app=asgiapp, client=("1.2.3.4", 123))  # type: ignore
    async with AsyncClient(
        transport=transport, base_url="http://example.com"
    ) as client:
        yield client


@pytest.fixture
async def graphql_client(app: FastAPI) -> AsyncClientSession:
    """Authenticated GraphQL codegen client for OS2mo."""
    return app.state.context["graphql_client"]
