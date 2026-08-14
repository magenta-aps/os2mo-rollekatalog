# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
"""Date ties break by uuid, in the same direction for current and future
candidates: the winner must not flip the day a future object becomes
current."""

from dataclasses import dataclass
from datetime import datetime
from datetime import timedelta
from typing import Optional
from uuid import UUID
from zoneinfo import ZoneInfo

from os2mo_rollekatalog.junkyard import select_preferred


@dataclass
class Validity:
    from_: datetime
    to: Optional[datetime]


@dataclass
class Version:
    uuid: UUID
    validity: Validity


SMALL = UUID("00000000-0000-4000-8000-000000000001")
BIG = UUID("ffffffff-ffff-4fff-bfff-fffffffffffe")


def test_uuid_tie_break_is_consistent_across_current_and_future() -> None:
    now = datetime.now(ZoneInfo("Europe/Copenhagen"))

    def contenders(start: datetime) -> list[Version]:
        return [Version(uuid, Validity(start, None)) for uuid in (SMALL, BIG)]

    future_winner = select_preferred(contenders(now + timedelta(days=100)))
    current_winner = select_preferred(contenders(now - timedelta(days=100)))
    assert future_winner is not None
    assert current_winner is not None
    assert future_winner.uuid == current_winner.uuid
