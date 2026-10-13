"""Tests for animated and fallback image output."""

import json
from datetime import date, timedelta
from pathlib import Path
from typing import Any

import pytest
from PIL import Image

import moonwalk_contributions.assets as assets
import moonwalk_contributions.pipeline as pipeline
from moonwalk_contributions.animation import (
    ENDING_FRAME_COUNT,
    ENDPOINT_FRAME_COUNT,
    SAMPLES_PER_CELL,
    SPIN_FRAME_COUNT,
    SPIN_INTERVAL_CELLS,
    AnimationSequence,
    build_animation,
)
from moonwalk_contributions.assets import save_animation
from moonwalk_contributions.github import GitHubAPIError, parse_contribution_calendar
from moonwalk_contributions.models import ContributionCalendar, ContributionDay

FIXTURE_PATH = Path(__file__).parent / "fixtures" / "contributions.json"


def _fixture_animation() -> AnimationSequence:
    payload: dict[str, Any] = json.loads(FIXTURE_PATH.read_text())
    return build_animation(parse_contribution_calendar(payload))


def test_save_animation_writes_looping_gif_and_static_png(tmp_path: Path) -> None:
    """Both formats are saved with the expected dimensions and frame count."""
    sequence = _fixture_animation()

    generated = save_animation(sequence, tmp_path / "assets")

    assert generated.animation.exists()
    assert generated.fallback.exists()
    with Image.open(generated.animation) as gif:
        assert gif.format == "GIF"
        assert gif.size == (sequence.width, sequence.height)
        assert gif.n_frames == len(sequence.frames)
        assert gif.info["loop"] == 0
    with Image.open(generated.fallback) as png:
        assert png.format == "PNG"
        assert png.size == (sequence.width, sequence.height)
    assert list((tmp_path / "assets").glob(".moonwalk-*")) == []


def test_full_year_animation_stays_within_readme_size_budget(tmp_path: Path) -> None:
    """A 53-week animation has the expected frame count and remains compact."""
    start = date(2025, 10, 5)
    levels = ["NONE", "FIRST_QUARTILE", "SECOND_QUARTILE", "THIRD_QUARTILE", "FOURTH_QUARTILE"]
    weeks = []
    for week_index in range(53):
        week = []
        for weekday in range(7):
            count = (week_index * 3 + weekday * 2) % 8
            level_index = min(4, (count + 1) // 2) if count else 0
            week.append(
                ContributionDay(
                    day=start + timedelta(days=week_index * 7 + weekday),
                    count=count,
                    level=levels[level_index],
                )
            )
        weeks.append(tuple(week))

    calendar = ContributionCalendar(
        total_contributions=sum(day.count for week in weeks for day in week),
        weeks=tuple(weeks),
    )
    sequence = build_animation(calendar)
    generated = save_animation(sequence, tmp_path)

    with Image.open(generated.animation) as gif:
        spin_count = (53 * 7 - 1) // SPIN_INTERVAL_CELLS
        # The encoder combines the identical moonwalk/first-spin images.
        assert gif.n_frames == (
            SAMPLES_PER_CELL * (53 * 7 - 1)
            + 1
            + ENDPOINT_FRAME_COUNT
            + ENDING_FRAME_COUNT
            + 1
            + spin_count * (SPIN_FRAME_COUNT - 1)
        )
        playback_ms = 0
        for index in range(gif.n_frames):
            gif.seek(index)
            playback_ms += gif.info["duration"]
        assert playback_ms == sum(sequence.durations_ms)
    assert generated.animation.stat().st_size <= assets.MAX_GIF_SIZE_BYTES


def test_oversized_gif_does_not_replace_existing_outputs(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Validation failures leave the previous GIF and PNG intact."""
    output_dir = tmp_path / "assets"
    output_dir.mkdir()
    gif_path = output_dir / "moonwalk-contributions.gif"
    png_path = output_dir / "moonwalk-contributions.png"
    gif_path.write_bytes(b"old-gif")
    png_path.write_bytes(b"old-png")
    monkeypatch.setattr(assets, "MAX_GIF_SIZE_BYTES", 1)

    with pytest.raises(ValueError, match="size limit"):
        save_animation(_fixture_animation(), output_dir)

    assert gif_path.read_bytes() == b"old-gif"
    assert png_path.read_bytes() == b"old-png"
    assert list(output_dir.glob(".moonwalk-*")) == []


def test_api_failure_does_not_replace_existing_outputs(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """The pipeline fetches and validates data before saving any image."""
    output_dir = tmp_path / "assets"
    output_dir.mkdir()
    gif_path = output_dir / "moonwalk-contributions.gif"
    png_path = output_dir / "moonwalk-contributions.png"
    gif_path.write_bytes(b"old-gif")
    png_path.write_bytes(b"old-png")

    def fail_fetch(username: str, token: str | None) -> None:
        raise GitHubAPIError("API unavailable")

    monkeypatch.setattr(pipeline, "fetch_contribution_calendar", fail_fetch)

    with pytest.raises(GitHubAPIError):
        pipeline.generate_contribution_assets("octocat", "token", output_dir)

    assert gif_path.read_bytes() == b"old-gif"
    assert png_path.read_bytes() == b"old-png"
