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
    # AMQP isn't consumed by the integration (events come via the GraphQL
    # event system) but fastramqpi 12.x still requires the AMQP system to
    # be configured. Keep the exchange/queue prefix here so the idle AMQP
    # consumer is named consistently.
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

    sync_enabled: bool = Field(
        False,
        description=(
            "Enable writes to rollekatalog. This is disabled by default to "
            "allow a smooth roll-out. Trigger all refresh events and let the "
            "integration populate its database before enabling sync."
        ),
    )

    listen_to_changes_in_mo: bool = Field(
        True,
        description=(
            "Declare GraphQL event listeners and process MO changes as they "
            "happen. On by default; the integration is event-driven and does "
            "nothing useful without it. Disabled in tests that drive the "
            "event endpoints directly so background fetchers don't race them."
        ),
    )

    rollekatalog_url: AnyHttpUrl = Field(description="Base url for Rollekatalog.")
    api_key: SecretStr = Field(description="API key for Rollekatalog.")
    interval: int = Field(
        60 * 15, description="The interval in which we sync to Rollekatalog."
    )
    root_org_unit: UUID = Field(
        description="Root in OS2mo. Only sync this org unit, and units below."
    )

    external_roots: list[UUID] = Field(
        [],
        description="List of external pseudo root UUIDs. Pseudo roots will be placed under ROOT_ORG_UNIT in Rollekatalog.",
    )

    ad_itsystem_user_keys: list[str] = Field(
        description=(
            "User keys of the AD-like itsystems in OS2mo to sync GUIDs from. "
            "Each is mapped to the FK itsystem the same way. Most customers have "
            "a single AD, but some have several (e.g. a separate 'Skole-AD'), so "
            "this is a list. Given as a JSON list, e.g. "
            '\'["Active Directory", "Skole-AD"]\'.'
        )
    )
    fk_itsystem_user_key: str = Field(
        description="Designed to sync AD GUIDs to Rollekatalog, this value represents the user key of the FK itsystem in OS2mo."
    )
    employee_email_user_key: str = Field(
        "EmailEmployee", description="User_key of the employee-email address-type"
    )
    mit_id_user_key: str = Field(
        "MitIDEmployee", description="User_key of the MitID address-type"
    )
    exclude_org_unit_level: UUID | None = Field(
        None,
        description="UUID of `org_unit_level` to ignore. If a unit has this level the unit (including it's children) will not be synced",
    )
    prefer_nickname: bool = Field(
        False,
        description="Whether to sync the *name* or *nickname* of OS2mo to Rollekatalog.",
    )
    sync_titles: bool = Field(
        False, description="Whether we should sync job titles objects to Rollekatalog."
    )

    ldap_url: AnyHttpUrl | None = Field(
        None, description="Optional base url for LDAP integration."
    )
    httpx_timeout: int = Field(30, description="Timeout when we sync to Rollekatalog.")
