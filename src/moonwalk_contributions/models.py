"""Typed models for GitHub contribution calendars."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True)
class ContributionDay:
    """Contribution count and display level for one calendar day."""

    day: date
    count: int
    level: str


@dataclass(frozen=True)
class ContributionCalendar:
    """Contribution days grouped into the weeks returned by GitHub."""

    total_contributions: int
    weeks: tuple[tuple[ContributionDay, ...], ...]

    @property
    def days(self) -> tuple[ContributionDay, ...]:
        """Return all days in chronological week order."""
        return tuple(day for week in self.weeks for day in week)
