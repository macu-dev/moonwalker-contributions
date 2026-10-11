"""Tests for the moonwalk and closing choreography sequence."""

import json
from pathlib import Path
from unittest.mock import patch

import pytest
from PIL import Image, ImageDraw

from moonwalk_contributions.animation import (
    ENDPOINT_FRAME_COUNT,
    FINAL_POSE_DURATION_MS,
    MOONWALK_FRAME_DURATION_MS,
    SAMPLES_PER_CELL,
    FramePhase,
    build_animation,
)
from moonwalk_contributions.github import parse_contribution_calendar
from moonwalk_contributions.models import ContributionCalendar
from moonwalk_contributions.render import (
    COLORS,
    MOONWALK_CYCLE_FRAMES,
    MOONWALK_SAMPLE_DISTANCE,
    draw_moonwalker,
    grid_layout,
    moonwalk_feet,
    render_contribution_grid,
    walking_feet,
)

FIXTURE_PATH = Path(__file__).parent / "fixtures" / "contributions.json"


def test_moonwalk_continues_across_the_entire_grid() -> None:
    """Endpoint glides bracket continuous moonwalk across every grid cell."""
    calendar = parse_contribution_calendar(json.loads(FIXTURE_PATH.read_text()))
    animation = build_animation(calendar)
    walk_frame_count = SAMPLES_PER_CELL * (7 * len(calendar.weeks) - 1) + 1
    phases = [frame.phase for frame in animation.frames]
    assert phases == (
        [FramePhase.MOONWALK_START] * ENDPOINT_FRAME_COUNT
        + [FramePhase.MOONWALK] * walk_frame_count
        + [FramePhase.MOONWALK_END] * ENDPOINT_FRAME_COUNT
        + [FramePhase.FINAL_POSE]
    )
    assert animation.durations_ms[-1] == FINAL_POSE_DURATION_MS
    assert all(frame.active_day is None for frame in animation.frames if frame.phase is not FramePhase.MOONWALK)


def test_moonwalk_highlights_every_day_and_connects_to_endpoint_dances() -> None:
    """Every source date glows during moonwalk and phase changes do not teleport."""
    calendar = parse_contribution_calendar(json.loads(FIXTURE_PATH.read_text()))
    animation = build_animation(calendar)
    walked_days = {frame.active_day for frame in animation.frames if frame.phase is FramePhase.MOONWALK}
    assert walked_days - {None} == {day.day for day in calendar.days}
    for first, second in zip(animation.frames, animation.frames[1:], strict=False):
        if first.phase is not second.phase:
            assert first.performer_position == second.performer_position
    walk = [frame for frame in animation.frames if frame.phase is FramePhase.MOONWALK]
    layout = grid_layout(calendar)
    assert walk[0].performer_position == layout.cell_center(0, 0)
    assert walk[-1].performer_position == layout.cell_center(len(calendar.weeks) - 1, 6)


def test_moonwalk_uses_distinct_alternating_heel_and_slide_poses() -> None:
    """The four frames follow alternating heel lifts and backward foot slides."""
    images = []
    for step_index in range(4):
        image = Image.new("RGB", (96, 96), COLORS["background"])
        draw_moonwalker(ImageDraw.Draw(image), 48, 48, step_index=step_index)
        images.append(image.tobytes())

    assert len(set(images)) == 4


def test_empty_calendar_cannot_be_animated() -> None:
    """An empty source calendar fails with a helpful error."""
    with pytest.raises(ValueError, match="no weeks"):
        build_animation(ContributionCalendar(total_contributions=0, weeks=()))


@pytest.mark.parametrize("facing", [-1, 1])
def test_support_toe_stays_planted_while_body_glides(facing: int) -> None:
    """Support stays on the floor; the flat foot moves at twice body speed."""
    for half_cycle in (0, 8):
        support_positions = []
        slide_positions = []
        for offset in range(6):
            feet = moonwalk_feet(half_cycle + offset)
            support = max(feet, key=lambda foot: foot.heel_lift)
            sliding = min(feet, key=lambda foot: foot.heel_lift)
            assert support.heel_lift == 9
            assert sliding.heel_lift == 0
            body_x = 100 - facing * MOONWALK_SAMPLE_DISTANCE * offset
            support_positions.append(body_x + facing * support.x)
            slide_positions.append(body_x + facing * sliding.x)
        assert max(support_positions) - min(support_positions) < 1e-9
        assert slide_positions[-1] - slide_positions[0] == pytest.approx(-2 * facing * MOONWALK_SAMPLE_DISTANCE * 5)
    assert moonwalk_feet(0)[0].raised_heel != moonwalk_feet(8)[0].raised_heel


@pytest.mark.parametrize("boundary", [8, 16])
def test_feet_do_not_teleport_at_weight_transfer_or_loop(boundary: int) -> None:
    """Both toe locations and heel heights must be continuous at exchanges."""
    before = moonwalk_feet(boundary - 0.0001)
    after = moonwalk_feet(boundary + 0.0001)
    for first, second in zip(before, after, strict=True):
        assert abs(second.x - first.x) < 0.001
        assert abs(second.heel_lift - first.heel_lift) < 0.001
    midway = moonwalk_feet(boundary - 1)
    assert midway[0].heel_lift == midway[1].heel_lift == 4.5


def test_every_moving_phase_uses_moonwalk_facing_backward() -> None:
    """All rows and both endpoint sequences must use backward moonwalk."""
    calendar = parse_contribution_calendar(json.loads(FIXTURE_PATH.read_text()))
    with patch("moonwalk_contributions.animation.render_contribution_grid", wraps=render_contribution_grid) as render:
        animation = build_animation(calendar)
    directions = set()
    for index, (current, following) in enumerate(zip(animation.frames, animation.frames[1:], strict=False)):
        if current.phase is FramePhase.FINAL_POSE:
            continue
        call = render.call_args_list[index]
        assert call.kwargs["dancer_pose"] == "moonwalk"
        feet = moonwalk_feet(call.kwargs["step_index"])
        assert all(foot.toe_lift == 0 for foot in feet)
        if current.phase is not following.phase:
            continue
        dx = following.performer_position[0] - current.performer_position[0]
        facing = call.kwargs["facing"]
        if dx:
            assert dx * facing < 0
            if current.phase is FramePhase.MOONWALK:
                directions.add(facing)
    assert directions == {-1, 1}
    assert MOONWALK_FRAME_DURATION_MS == 50


def test_walking_lifts_the_free_foot_and_alternates_support() -> None:
    """A forward walk has an airborne return, unlike the moonwalk glide."""
    for first, second in ((0, 4), (4, 0)):
        stance_index = 0 if first == 0 else 1
        feet = walking_feet(first + 2)
        assert feet[stance_index].toe_lift == 0
        assert feet[1 - stance_index].toe_lift > 8
        assert walking_feet(second + 2)[stance_index].toe_lift > 8


def test_reference_outfit_and_torso_remain_stable_during_glide() -> None:
    """The cream suit and blue shirt retain a fixed upper body over the gait."""
    upper_bodies = []
    for step_index in range(MOONWALK_CYCLE_FRAMES):
        image = Image.new("RGB", (120, 120), COLORS["background"])
        draw_moonwalker(ImageDraw.Draw(image), 60, 60, step_index=step_index)
        upper_bodies.append(image.crop((30, 10, 90, 60)).tobytes())
        colors = {color for _, color in image.getcolors() or []}
        assert (217, 215, 186) in colors
        assert (89, 109, 145) in colors
    assert len(set(upper_bodies)) == 1


def test_rendered_support_stays_fixed_through_horizontal_interpolation() -> None:
    """Integer rounding in actual frames must not make the support skate."""
    calendar = parse_contribution_calendar(json.loads(FIXTURE_PATH.read_text()))
    with patch("moonwalk_contributions.animation.render_contribution_grid", wraps=render_contribution_grid) as render:
        animation = build_animation(calendar)
    # First six horizontal samples cover one planted-toe glide.
    contacts = []
    for frame, call in zip(animation.frames[:6], render.call_args_list[:6], strict=True):
        feet = moonwalk_feet(call.kwargs["step_index"])
        support = max(feet, key=lambda foot: foot.heel_lift)
        contacts.append(frame.performer_position[0] + call.kwargs["facing"] * round(support.x))
    assert max(contacts) - min(contacts) <= 1


def test_support_remains_planted_during_grid_moonwalk() -> None:
    """The restored grid pass must preserve moonwalk ground contact."""
    calendar = parse_contribution_calendar(json.loads(FIXTURE_PATH.read_text()))
    with patch("moonwalk_contributions.animation.render_contribution_grid", wraps=render_contribution_grid) as render:
        animation = build_animation(calendar)
    contacts = []
    start = ENDPOINT_FRAME_COUNT
    for frame, call in zip(animation.frames[start : start + 6], render.call_args_list[start : start + 6], strict=True):
        support = max(moonwalk_feet(call.kwargs["step_index"]), key=lambda foot: foot.heel_lift)
        contacts.append(frame.performer_position[0] + call.kwargs["facing"] * round(support.x))
    assert max(contacts) - min(contacts) <= 1
