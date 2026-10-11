"""Read a user's contribution calendar from GitHub's GraphQL API."""

from __future__ import annotations

import json
from collections.abc import Mapping, Sequence
from datetime import UTC, date, datetime, timedelta
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from moonwalk_contributions.models import ContributionCalendar, ContributionDay

GRAPHQL_ENDPOINT = "https://api.github.com/graphql"
REQUEST_TIMEOUT_SECONDS = 20
CONTRIBUTION_LEVELS = {
    "NONE",
    "FIRST_QUARTILE",
    "SECOND_QUARTILE",
    "THIRD_QUARTILE",
    "FOURTH_QUARTILE",
}
CONTRIBUTION_QUERY = """
query ContributionCalendar($login: String!, $from: DateTime!, $to: DateTime!) {
  user(login: $login) {
    contributionsCollection(from: $from, to: $to) {
      contributionCalendar {
        totalContributions
        weeks {
          contributionDays {
            date
            contributionCount
            contributionLevel
          }
        }
      }
    }
  }
}
"""


class GitHubAPIError(RuntimeError):
    """Raised when GitHub cannot provide a valid contribution calendar."""


def parse_contribution_calendar(payload: Mapping[str, Any]) -> ContributionCalendar:
    """Validate and convert a GraphQL response into typed calendar data."""
    data = _mapping(payload.get("data"), "data")
    user = _mapping(data.get("user"), "data.user")
    collection = _mapping(user.get("contributionsCollection"), "contributionsCollection")
    calendar = _mapping(collection.get("contributionCalendar"), "contributionCalendar")
    raw_weeks = _sequence(calendar.get("weeks"), "contributionCalendar.weeks")
    total = _non_negative_int(calendar.get("totalContributions"), "totalContributions")

    weeks: list[tuple[ContributionDay, ...]] = []
    for week_index, raw_week in enumerate(raw_weeks):
        week = _mapping(raw_week, f"weeks[{week_index}]")
        raw_days = _sequence(week.get("contributionDays"), f"weeks[{week_index}].contributionDays")
        days = tuple(
            _parse_day(raw_day, f"weeks[{week_index}].contributionDays[{day_index}]")
            for day_index, raw_day in enumerate(raw_days)
        )
        weeks.append(days)

    return ContributionCalendar(total_contributions=total, weeks=tuple(weeks))


def fetch_contribution_calendar(
    username: str,
    token: str | None,
    *,
    today: date | None = None,
) -> ContributionCalendar:
    """Fetch the latest year of contribution data for a GitHub account."""
    normalized_username = username.strip()
    if not normalized_username:
        raise GitHubAPIError("A GitHub username is required.")
    if not token or not token.strip():
        raise GitHubAPIError("GitHub GraphQL requires authentication. Set GITHUB_TOKEN and try again.")

    end_date = today or datetime.now(UTC).date()
    start_date = end_date - timedelta(days=365)
    variables = {
        "login": normalized_username,
        "from": _at_utc_midnight(start_date),
        "to": _at_utc_midnight(end_date + timedelta(days=1)),
    }
    request = Request(
        GRAPHQL_ENDPOINT,
        data=json.dumps({"query": CONTRIBUTION_QUERY, "variables": variables}).encode("utf-8"),
        headers={
            "Accept": "application/json",
            "Authorization": f"Bearer {token.strip()}",
            "Content-Type": "application/json",
            "User-Agent": "moonwalk-contributions",
        },
        method="POST",
    )

    try:
        with urlopen(request, timeout=REQUEST_TIMEOUT_SECONDS) as response:
            response_data = json.loads(response.read())
    except HTTPError as error:
        if error.code in (401, 403):
            raise GitHubAPIError("GitHub rejected the token. Check its validity and permissions.") from None
        raise GitHubAPIError(f"GitHub returned HTTP {error.code} while fetching contributions.") from None
    except (URLError, TimeoutError, OSError):
        raise GitHubAPIError("Could not reach GitHub to fetch contributions.") from None
    except json.JSONDecodeError:
        raise GitHubAPIError("GitHub returned an invalid JSON response.") from None

    if not isinstance(response_data, Mapping):
        raise GitHubAPIError("GitHub returned an invalid response shape.")
    if response_data.get("errors"):
        raise GitHubAPIError(
            "GitHub could not read this contribution calendar. Check the username and token permissions."
        )
    try:
        return parse_contribution_calendar(response_data)
    except (KeyError, TypeError, ValueError) as error:
        raise GitHubAPIError(f"GitHub returned an invalid contribution calendar: {error}") from None


def _parse_day(value: Any, field: str) -> ContributionDay:
    day_data = _mapping(value, field)
    try:
        contribution_date = date.fromisoformat(_string(day_data.get("date"), f"{field}.date"))
    except ValueError as error:
        raise ValueError(f"{field}.date must be an ISO date") from error
    count = _non_negative_int(day_data.get("contributionCount"), f"{field}.contributionCount")
    level = _string(day_data.get("contributionLevel"), f"{field}.contributionLevel")
    if level not in CONTRIBUTION_LEVELS:
        raise ValueError(f"{field}.contributionLevel is not recognized")
    return ContributionDay(day=contribution_date, count=count, level=level)


def _mapping(value: Any, field: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise TypeError(f"{field} must be an object")
    return value


def _sequence(value: Any, field: str) -> Sequence[Any]:
    if not isinstance(value, list):
        raise TypeError(f"{field} must be a list")
    return value


def _string(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value:
        raise TypeError(f"{field} must be a non-empty string")
    return value


def _non_negative_int(value: Any, field: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise TypeError(f"{field} must be a non-negative integer")
    return value


def _at_utc_midnight(day: date) -> str:
    return datetime.combine(day, datetime.min.time(), tzinfo=UTC).isoformat().replace("+00:00", "Z")
