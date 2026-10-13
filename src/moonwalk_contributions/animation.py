"""Build the moonwalk and closing choreography as ordered image frames."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from enum import StrEnum

from PIL import Image

from moonwalk_contributions.models import ContributionCalendar, ContributionDay
from moonwalk_contributions.render import (
    CANVAS_HEIGHT,
    CANVAS_WIDTH,
    MOONWALK_CYCLE_FRAMES,
    MOONWALK_SAMPLE_DISTANCE,
    grid_layout,
    render_contribution_grid,
)

MOONWALK_FRAME_DURATION_MS = 50
SAMPLES_PER_CELL = 4
SPIN_INTERVAL_CELLS = 24
SPIN_FRAME_COUNT = 16
FINAL_POSE_DURATION_MS = 1_000
ENDPOINT_FRAME_COUNT = MOONWALK_CYCLE_FRAMES + 1
ENDING_GLIDE_DISTANCE = MOONWALK_SAMPLE_DISTANCE * 2
ENDING_FRAME_COUNT = round(ENDING_GLIDE_DISTANCE / MOONWALK_SAMPLE_DISTANCE) + 1


class FramePhase(StrEnum):
    """Narrative phase represented by an animation frame."""

    MOONWALK_START = "moonwalk_start"
    MOONWALK = "moonwalk"
    SPIN = "spin"
    MOONWALK_END = "moonwalk_end"
    FINAL_POSE = "final_pose"


@dataclass(frozen=True)
class AnimationFrame:
    """One rendered image and its place in the dance sequence."""

    image: Image.Image
    phase: FramePhase
    active_day: date | None
    performer_position: tuple[int, int]


@dataclass(frozen=True)
class AnimationSequence:
    """Ordered animation frames with their playback durations."""

    frames: tuple[AnimationFrame, ...]
    durations_ms: tuple[int, ...]
    width: int = CANVAS_WIDTH
    height: int = CANVAS_HEIGHT


def build_animation(calendar: ContributionCalendar) -> AnimationSequence:
    """Moonwalk across every glowing tile, with short entrance and exit glides."""
    if not calendar.weeks:
        raise ValueError("The contribution calendar has no weeks to animate.")

    layout = grid_layout(calendar)
    days_by_cell = _days_by_cell(calendar)
    frames: list[AnimationFrame] = []
    durations: list[int] = []

    traversal: list[tuple[int, int]] = []
    for row in range(7):
        week_indexes = range(layout.columns) if row % 2 == 0 else range(layout.columns - 1, -1, -1)
        traversal.extend((week_index, row) for week_index in week_indexes)

    first_position = layout.cell_center(*traversal[0])
    _append_endpoint_moonwalk(
        calendar, frames, durations, (first_position[0] + 56, first_position[1]), FramePhase.MOONWALK_START
    )

    for cell_index, (week_index, weekday) in enumerate(traversal):
        center = layout.cell_center(week_index, weekday)
        contribution = days_by_cell.get((week_index, weekday))
        facing = -1 if weekday % 2 == 0 else 1
        step_index = (cell_index % layout.columns) * SAMPLES_PER_CELL
        if cell_index + 1 < len(traversal):
            next_week, next_weekday = traversal[cell_index + 1]
            next_center = layout.cell_center(next_week, next_weekday)
            samples = SAMPLES_PER_CELL
        else:
            next_center = center
            samples = 1
        for sample in range(samples):
            fraction = sample / SAMPLES_PER_CELL
            position = (
                round(center[0] + (next_center[0] - center[0]) * fraction),
                round(center[1] + (next_center[1] - center[1]) * fraction),
            )
            # Hold the gait during vertical row changes; horizontal distance
            # alone drives foot phase, so feet do not shuffle at the edge.
            gait_step = step_index + abs(position[0] - center[0]) / MOONWALK_SAMPLE_DISTANCE
            frames.append(
                _render_frame(
                    calendar,
                    position,
                    FramePhase.MOONWALK,
                    contribution.day if contribution else None,
                    gait_step,
                    "moonwalk",
                    facing,
                )
            )
            durations.append(MOONWALK_FRAME_DURATION_MS)
            if sample == 0 and (cell_index + 1) % SPIN_INTERVAL_CELLS == 0 and cell_index + 1 < len(traversal):
                for spin_sample in range(SPIN_FRAME_COUNT):
                    frames.append(
                        _render_frame(
                            calendar,
                            position,
                            FramePhase.SPIN,
                            contribution.day if contribution else None,
                            gait_step,
                            "spin",
                            facing,
                            spin_progress=spin_sample / (SPIN_FRAME_COUNT - 1),
                        )
                    )
                    durations.append(MOONWALK_FRAME_DURATION_MS)

    final_position = layout.cell_center(*traversal[-1])
    _append_endpoint_moonwalk(
        calendar,
        frames,
        durations,
        final_position,
        FramePhase.MOONWALK_END,
        distance=ENDING_GLIDE_DISTANCE,
        frame_count=ENDING_FRAME_COUNT,
    )
    final_pose_position = frames[-1].performer_position
    frames.append(_render_frame(calendar, final_pose_position, FramePhase.FINAL_POSE, None, 0, "final"))
    durations.append(FINAL_POSE_DURATION_MS)

    return AnimationSequence(frames=tuple(frames), durations_ms=tuple(durations))


def _append_endpoint_moonwalk(
    calendar: ContributionCalendar,
    frames: list[AnimationFrame],
    durations: list[int],
    start: tuple[int, int],
    phase: FramePhase,
    *,
    distance: float = MOONWALK_CYCLE_FRAMES * MOONWALK_SAMPLE_DISTANCE,
    frame_count: int = ENDPOINT_FRAME_COUNT,
) -> None:
    """Append one backward glide beside an endpoint, including its arrival."""
    for sample in range(frame_count):
        travelled = round(sample * distance / (frame_count - 1)) if frame_count > 1 else 0
        position = (start[0] - travelled, start[1])
        frames.append(
            _render_frame(calendar, position, phase, None, travelled / MOONWALK_SAMPLE_DISTANCE, "moonwalk", 1)
        )
        durations.append(MOONWALK_FRAME_DURATION_MS)


def _days_by_cell(calendar: ContributionCalendar) -> dict[tuple[int, int], ContributionDay]:
    days: dict[tuple[int, int], ContributionDay] = {}
    for week_index, week in enumerate(calendar.weeks):
        for contribution in week:
            weekday = (contribution.day.weekday() + 1) % 7
            days[(week_index, weekday)] = contribution
    return days


def _render_frame(
    calendar: ContributionCalendar,
    performer_position: tuple[int, int],
    phase: FramePhase,
    active_day: date | None,
    step_index: float,
    pose: str,
    facing: int = 1,
    *,
    spin_progress: float = 0,
) -> AnimationFrame:
    image = render_contribution_grid(
        calendar,
        highlighted_day=active_day,
        performer_at=performer_position,
        dancer_pose=pose,
        step_index=step_index,
        facing=facing,
        spin_progress=spin_progress,
        width=CANVAS_WIDTH,
        height=CANVAS_HEIGHT,
    )
    return AnimationFrame(
        image=image,
        phase=phase,
        active_day=active_day,
        performer_position=performer_position,
    )
