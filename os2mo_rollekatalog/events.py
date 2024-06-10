# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
import structlog
from fastramqpi.ramqp.mo import MORouter

from os2mo_rollekatalog import depends
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
