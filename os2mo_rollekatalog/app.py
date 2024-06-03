# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from typing import Any

from fastapi import FastAPI
from fastramqpi.main import FastRAMQPI

from os2mo_rollekatalog import api
from os2mo_rollekatalog import events
from os2mo_rollekatalog.autogenerated_graphql_client import GraphQLClient
from os2mo_rollekatalog.config import Settings


def create_app(**kwargs: Any) -> FastAPI:
    settings = Settings(**kwargs)
    fastramqpi = FastRAMQPI(
        application_name="rollekatalog",
        settings=settings.fastramqpi,
        graphql_version=22,
        graphql_client_cls=GraphQLClient,
    )
    fastramqpi.add_context(settings=settings)
    # context = fastramqpi.get_context()

    # FastAPI router
    app = fastramqpi.get_app()
    app.include_router(api.router)

    # MO AMQP
    mo_amqp_system = fastramqpi.get_amqpsystem()
    mo_amqp_system.router.registry.update(events.router.registry)

    return app
