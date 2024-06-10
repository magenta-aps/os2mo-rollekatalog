# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from fastramqpi.config import Settings as FastRAMQPISettings
from pydantic import BaseSettings
from pydantic import Field


class _Settings(BaseSettings):
    class Config:
        frozen = True
        env_nested_delimiter = "__"

    fastramqpi: FastRAMQPISettings

    itsystem_user_key: str = Field(
        description="Designed to sync AD GUIDs to Rollekatalog, this value represents the user key of the AD itsystem in OS2mo."
    )
    use_nickname: bool = Field(
        False,
        description="Whether to sync the *name* or *nickname* of OS2mo to Rollekatalog.",
    )
    sync_titles: bool = Field(
        False, description="Whether we should sync job titles objects to Rollekatalog."
    )