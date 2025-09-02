# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from uuid import UUID

from fastramqpi.config import Settings as _FastRAMQPISettings
from fastramqpi.ramqp.config import AMQPConnectionSettings
from pydantic import AnyHttpUrl
from pydantic import BaseSettings
from pydantic import Field
from pydantic import SecretStr


class AMQPConnectionSettingsSeeded(AMQPConnectionSettings):
    exchange = "os2mo_rollekatalog"
    queue_prefix = "os2mo_rollekatalog"
    upstream_exchange = "os2mo"


class FastRAMQPISettings(_FastRAMQPISettings):
    amqp: AMQPConnectionSettingsSeeded


class _Settings(BaseSettings):
    class Config:
        frozen = True
        env_nested_delimiter = "__"

    fastramqpi: FastRAMQPISettings

    rollekatalog_url: AnyHttpUrl = Field(description="Base url for Rollekatalog.")
    api_key: SecretStr = Field(description="API key for Rollekatalog.")
    interval: int = Field(
        60 * 15, description="The interval in which we sync to Rollekatalog."
    )
    root_org_unit: UUID = Field(
        description="Root in OS2mo. Only sync this org unit, and units below."
    )

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
