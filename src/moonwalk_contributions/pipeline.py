"""Coordinate data retrieval, rendering, and asset generation."""

from __future__ import annotations

from pathlib import Path

from moonwalk_contributions.animation import build_animation
from moonwalk_contributions.assets import GeneratedAssets, save_animation
from moonwalk_contributions.github import fetch_contribution_calendar


def generate_contribution_assets(
    username: str,
    token: str | None,
    output_dir: Path,
) -> GeneratedAssets:
    """Fetch contributions and generate image files after data validation."""
    calendar = fetch_contribution_calendar(username, token)
    animation = build_animation(calendar)
    return save_animation(animation, output_dir)
