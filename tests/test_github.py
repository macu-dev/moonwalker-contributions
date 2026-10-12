"""Tests for the GitHub contribution calendar client."""

import json
from datetime import date
from io import BytesIO
from pathlib import Path
from typing import Any, Self
from urllib.error import HTTPError

import pytest
from PIL import ImageColor

import moonwalk_contributions.github as github
from moonwalk_contributions.github import (
    GitHubAPIError,
    fetch_contribution_calendar,
    parse_contribution_calendar,
)
from moonwalk_contributions.render import COLORS, _load_font, grid_layout, render_contribution_grid

FIXTURE_PATH = Path(__file__).parent / "fixtures" / "contributions.json"


def test_render_font_supports_spanish_accented_letters() -> None:
    """Accented Spanish letters use real glyphs instead of replacement boxes."""
    font = _load_font(12)

    assert bytes(font.getmask("ú")) != bytes(font.getmask("?"))
    assert bytes(font.getmask("ñ")) != bytes(font.getmask("?"))


def test_parse_calendar_preserves_weeks_dates_levels_and_empty_days() -> None:
    """Calendar conversion retains the day groupings and activity levels."""
    payload = json.loads(FIXTURE_PATH.read_text())

    calendar = parse_contribution_calendar(payload)

    assert calendar.total_contributions == 4
    assert [len(week) for week in calendar.weeks] == [3, 2]
    assert [day.day.isoformat() for day in calendar.days] == [
        "2026-10-04",
        "2026-10-05",
        "2026-10-06",
        "2026-10-07",
        "2026-10-08",
    ]
    assert [day.count for day in calendar.days] == [0, 1, 3, 0, 0]
    assert calendar.days[2].level == "FOURTH_QUARTILE"


def test_fetch_requires_token_before_network_request() -> None:
    """Missing API credentials produce a clear error without a request."""
    with pytest.raises(GitHubAPIError, match="Set GITHUB_TOKEN"):
        fetch_contribution_calendar("octocat", None, today=date(2026, 10, 9))


def test_fixture_is_a_valid_graphql_response() -> None:
    """The checked-in response fixture can be parsed by the public model."""
    payload: dict[str, Any] = json.loads(FIXTURE_PATH.read_text())

    assert parse_contribution_calendar(payload).days[1].count == 1


@pytest.mark.parametrize(
    "payload",
    [
        {},
        {"data": {"user": None}},
        {
            "data": {
                "user": {
                    "contributionsCollection": {
                        "contributionCalendar": {
                            "totalContributions": -1,
                            "weeks": [],
                        }
                    }
                }
            }
        },
    ],
)
def test_invalid_graphql_payloads_raise_clear_errors(payload: dict[str, Any]) -> None:
    """Malformed API data is rejected before it can reach the renderer."""
    with pytest.raises((TypeError, ValueError)):
        parse_contribution_calendar(payload)


def test_http_authentication_error_does_not_expose_token(monkeypatch: pytest.MonkeyPatch) -> None:
    """Authentication failures return a safe message without the token."""
    secret = "sensitive-token-value"

    def raise_auth_error(*args: Any, **kwargs: Any) -> None:
        raise HTTPError("https://api.github.com/graphql", 401, "Unauthorized", {}, BytesIO(b""))

    monkeypatch.setattr(github, "urlopen", raise_auth_error)

    with pytest.raises(GitHubAPIError) as error:
        fetch_contribution_calendar("octocat", secret, today=date(2026, 10, 9))

    assert secret not in str(error.value)
    assert "token" in str(error.value).lower()


def test_fetch_error_does_not_modify_existing_generated_assets(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """A failed data fetch leaves previously generated resources untouched."""
    existing_asset = tmp_path / "assets" / "moonwalk.gif"
    existing_asset.parent.mkdir()
    existing_asset.write_bytes(b"last-known-good-image")

    def raise_auth_error(*args: Any, **kwargs: Any) -> None:
        raise HTTPError("https://api.github.com/graphql", 401, "Unauthorized", {}, BytesIO(b""))

    monkeypatch.setattr(github, "urlopen", raise_auth_error)

    with pytest.raises(GitHubAPIError):
        fetch_contribution_calendar("octocat", "test-token", today=date(2026, 10, 9))

    assert existing_asset.read_bytes() == b"last-known-good-image"


def test_graphql_errors_are_reported_without_raw_response(monkeypatch: pytest.MonkeyPatch) -> None:
    """GraphQL error bodies are not copied into user-facing output."""
    secret = "sensitive-token-value"
    error_payload = {"errors": [{"message": f"request {secret} denied"}]}

    class FakeResponse:
        def __enter__(self) -> Self:
            return self

        def __exit__(self, *args: object) -> None:
            return None

        def read(self) -> bytes:
            return json.dumps(error_payload).encode("utf-8")

    def fake_urlopen(*args: Any, **kwargs: Any) -> FakeResponse:
        return FakeResponse()

    monkeypatch.setattr(github, "urlopen", fake_urlopen)

    with pytest.raises(GitHubAPIError) as error:
        fetch_contribution_calendar("octocat", secret, today=date(2026, 10, 9))

    assert secret not in str(error.value)


def test_render_uses_distinct_base_colors_for_activity_levels() -> None:
    """The daily contribution level remains visible in the base grid."""
    payload: dict[str, Any] = json.loads(FIXTURE_PATH.read_text())
    calendar = parse_contribution_calendar(payload)
    layout = grid_layout(calendar)
    image = render_contribution_grid(calendar)

    empty_x, empty_y = layout.cell_center(0, 0)
    low_x, low_y = layout.cell_center(0, 1)
    high_x, high_y = layout.cell_center(0, 2)

    assert image.size == (960, 248)
    assert image.getpixel((empty_x, empty_y)) == ImageColor.getrgb(COLORS["grid_base"])
    assert image.getpixel((low_x, low_y)) == ImageColor.getrgb(COLORS["FIRST_QUARTILE"])
    assert image.getpixel((high_x, high_y)) == ImageColor.getrgb(COLORS["FOURTH_QUARTILE"])


def test_tile_glow_preserves_levels_and_turns_off_after_a_step() -> None:
    """Visited tiles brighten with a halo, retain distinct levels and recover."""
    calendar = parse_contribution_calendar(json.loads(FIXTURE_PATH.read_text()))
    layout = grid_layout(calendar)
    base = render_contribution_grid(calendar, performer_at=(30, 150))
    bright_colors = set()
    for weekday in (0, 1, 2):
        day = calendar.weeks[0][weekday].day
        bright = render_contribution_grid(calendar, highlighted_day=day, performer_at=(30, 150))
        x, y = layout.cell_center(0, weekday)
        original = base.getpixel((x, y))
        glowing = bright.getpixel((x, y))
        assert sum(glowing) > sum(original)
        assert bright.getpixel((x + 7, y)) == ImageColor.getrgb(COLORS["highlight"])
        bright_colors.add(glowing)
        other_day = calendar.weeks[0][(weekday + 1) % 3].day
        following = render_contribution_grid(calendar, highlighted_day=other_day, performer_at=(30, 150))
        assert following.getpixel((x, y)) == original
    assert len(bright_colors) == 3
