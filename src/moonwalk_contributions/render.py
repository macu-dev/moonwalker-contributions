"""Draw a citypop contribution grid and its moonwalking performer."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from math import pi, sin
from pathlib import Path

from PIL import Image, ImageColor, ImageDraw, ImageFont

from moonwalk_contributions.models import ContributionCalendar, ContributionDay

CANVAS_WIDTH = 960
CANVAS_HEIGHT = 248
CELL_SIZE = 10
CELL_GAP = 4
GRID_TOP = 104
GRID_BOTTOM = 20
WEEKDAY_LABELS = {1: "lun", 3: "mié", 5: "vie"}
MONTH_LABELS = ("ene", "feb", "mar", "abr", "may", "jun", "jul", "ago", "sep", "oct", "nov", "dic")
Font = ImageFont.ImageFont | ImageFont.FreeTypeFont
FONT_PATH = Path(__file__).parent / "fonts" / "IBMPlexSans.ttf"


def _load_font(size: int) -> Font:
    """Load the bundled font with full Spanish character support."""
    return ImageFont.truetype(str(FONT_PATH), size=size)


COLORS = {
    "background": "#100d20",
    "grid_base": "#28223b",
    "FIRST_QUARTILE": "#58377a",
    "SECOND_QUARTILE": "#8750ad",
    "THIRD_QUARTILE": "#c35cc1",
    "FOURTH_QUARTILE": "#ff78bd",
    "highlight": "#fff0a8",
    "performer": "#fff0f7",
    "performer_shadow": "#4d315d",
    "accent": "#ff72bd",
    "horizon": "#432c64",
    "star": "#b78cda",
    "label": "#b8adc9",
    "legend": "#d9d2e3",
}


@dataclass(frozen=True)
class GridLayout:
    """Pixel geometry used to draw and inspect the contribution grid."""

    origin_x: int
    origin_y: int
    cell_size: int
    cell_gap: int
    columns: int

    def cell_center(self, week_index: int, weekday: int) -> tuple[int, int]:
        """Return the center point for a week and Sunday-first weekday index."""
        pitch = self.cell_size + self.cell_gap
        return (
            self.origin_x + week_index * pitch + self.cell_size // 2,
            self.origin_y + weekday * pitch + self.cell_size // 2,
        )


def grid_layout(calendar: ContributionCalendar, width: int = CANVAS_WIDTH) -> GridLayout:
    """Calculate a centered grid layout for a contribution calendar."""
    columns = max(1, len(calendar.weeks))
    pitch = CELL_SIZE + CELL_GAP
    content_width = columns * pitch - CELL_GAP
    origin_x = max(20, (width - content_width) // 2)
    return GridLayout(
        origin_x=origin_x,
        origin_y=GRID_TOP,
        cell_size=CELL_SIZE,
        cell_gap=CELL_GAP,
        columns=columns,
    )


def render_contribution_grid(
    calendar: ContributionCalendar,
    *,
    highlighted_day: date | None = None,
    performer_at: tuple[int, int] | None = None,
    dancer_pose: str = "moonwalk",
    step_index: float = 0,
    facing: int = 1,
    width: int = CANVAS_WIDTH,
    height: int = CANVAS_HEIGHT,
) -> Image.Image:
    """Render contribution levels as a dark neon calendar with a performer."""
    image = Image.new("RGB", (width, height), COLORS["background"])
    draw = ImageDraw.Draw(image)
    layout = grid_layout(calendar, width)
    pitch = layout.cell_size + layout.cell_gap
    grid_width = layout.columns * pitch - layout.cell_gap
    draw.line(
        (
            layout.origin_x - 2,
            layout.origin_y + 7 * pitch + 4,
            layout.origin_x + grid_width,
            layout.origin_y + 7 * pitch + 4,
        ),
        fill=COLORS["horizon"],
        width=1,
    )
    _draw_stars(draw, width, height)

    font = _load_font(12)
    draw.text(
        (layout.origin_x, 12),
        f"{calendar.total_contributions:,}".replace(",", ".") + " contribuciones en el último año",
        fill=COLORS["legend"],
        font=font,
    )
    _draw_calendar_labels(draw, calendar, layout, width, font)

    for week_index, week in enumerate(calendar.weeks):
        for contribution in week:
            weekday = (contribution.day.weekday() + 1) % 7
            center_x, center_y = layout.cell_center(week_index, weekday)
            fill = _level_color(contribution)
            radius = layout.cell_size // 2
            if highlighted_day == contribution.day:
                draw.rounded_rectangle(
                    (center_x - 8, center_y - 8, center_x + 8, center_y + 8), radius=4, fill="#66435b"
                )
                draw.rounded_rectangle(
                    (center_x - 7, center_y - 7, center_x + 7, center_y + 7),
                    radius=3,
                    outline=COLORS["highlight"],
                    width=2,
                )
                base = ImageColor.getrgb(fill)
                accent = ImageColor.getrgb(COLORS["highlight"])
                fill = "#" + "".join(
                    f"{round(channel * 0.6 + light * 0.4):02x}" for channel, light in zip(base, accent, strict=True)
                )
            draw.rounded_rectangle(
                (
                    center_x - radius,
                    center_y - radius,
                    center_x + radius,
                    center_y + radius,
                ),
                radius=2,
                fill=fill,
            )

    if calendar.days:
        center_x, center_y = performer_at or _performer_anchor(calendar, layout)
        _draw_readme_sized_performer(image, center_x, center_y - 37, dancer_pose, step_index, facing)
    _draw_activity_legend(draw, width, height, font)
    return image


def _draw_calendar_labels(
    draw: ImageDraw.ImageDraw,
    calendar: ContributionCalendar,
    layout: GridLayout,
    width: int,
    font: Font,
) -> None:
    """Add GitHub-like weekday and month labels around the contribution grid."""
    for weekday, label in WEEKDAY_LABELS.items():
        bounds = draw.textbbox((0, 0), label, font=font)
        label_width = bounds[2] - bounds[0]
        center_y = layout.cell_center(0, weekday)[1]
        draw.text(
            (layout.origin_x - label_width - 6, center_y - (bounds[3] - bounds[1]) // 2),
            label,
            fill=COLORS["label"],
            font=font,
        )

    previous_month: int | None = None
    for week_index, week in enumerate(calendar.weeks):
        if not week:
            continue
        month = week[0].day.month
        if month == previous_month:
            continue
        previous_month = month
        label = MONTH_LABELS[month - 1]
        bounds = draw.textbbox((0, 0), label, font=font)
        label_width = bounds[2] - bounds[0]
        center_x = layout.cell_center(week_index, 0)[0]
        left = max(layout.origin_x, min(width - label_width, center_x - label_width // 2))
        draw.text((left, GRID_TOP - 18), label, fill=COLORS["label"], font=font)


def _draw_activity_legend(
    draw: ImageDraw.ImageDraw,
    width: int,
    height: int,
    font: Font,
) -> None:
    """Show the five activity levels as a compact scale below the calendar."""
    low_label, high_label = "Menos", "Más"
    low_bounds = draw.textbbox((0, 0), low_label, font=font)
    high_bounds = draw.textbbox((0, 0), high_label, font=font)
    low_width = low_bounds[2] - low_bounds[0]
    high_width = high_bounds[2] - high_bounds[0]
    swatch_size = 8
    swatch_gap = 4
    label_gap = 7
    swatches_width = 5 * swatch_size + 4 * swatch_gap
    total_width = low_width + label_gap + swatches_width + label_gap + high_width
    x = (width - total_width) // 2
    y = height - GRID_BOTTOM - 11
    draw.text((x, y), low_label, fill=COLORS["label"], font=font)
    x += low_width + label_gap
    for color in ("grid_base", "FIRST_QUARTILE", "SECOND_QUARTILE", "THIRD_QUARTILE", "FOURTH_QUARTILE"):
        draw.rounded_rectangle((x, y + 1, x + swatch_size, y + 1 + swatch_size), radius=2, fill=COLORS[color])
        x += swatch_size + swatch_gap
    x -= swatch_gap
    x += label_gap
    draw.text((x, y), high_label, fill=COLORS["label"], font=font)


def _draw_readme_sized_performer(
    image: Image.Image,
    center_x: int,
    center_y: int,
    pose: str,
    step_index: float,
    facing: int,
) -> None:
    """Composite a crisp pixel-art performer without smoothing its edges."""
    sprite = Image.new("RGBA", (120, 120), (0, 0, 0, 0))
    draw_moonwalker(ImageDraw.Draw(sprite), 60, 60, pose=pose, step_index=step_index, facing=facing)
    image.paste(sprite, (center_x - 60, center_y - 60), sprite)


MOONWALK_CYCLE_FRAMES = 16
MOONWALK_SAMPLE_DISTANCE = 3.5


@dataclass(frozen=True)
class MoonwalkFoot:
    """Toe contact relative to the body and heel height above the floor."""

    x: float
    heel_lift: float
    toe_lift: float = 0

    @property
    def raised_heel(self) -> bool:
        """Whether the heel is above the floor."""
        return self.heel_lift > 0


def moonwalk_feet(step_index: float) -> tuple[MoonwalkFoot, MoonwalkFoot]:
    """Evaluate continuous toe positions and heel exchange across a full stride.

    Each half stride moves the support toe forward relative to the body and
    the flat toe backward by equal amounts. With backward body travel this
    keeps support fixed on the floor and moves the glide at twice body speed.
    Heel exchange happens at the end of a half stride without resetting toes.
    """
    phase = step_index % MOONWALK_CYCLE_FRAMES
    progress = (phase % 8) / 8
    exchange = max(0.0, (progress - 0.75) / 0.25)
    support = MoonwalkFoot(-14 + 28 * progress, 9 * (1 - exchange))
    sliding = MoonwalkFoot(14 - 28 * progress, 9 * exchange)
    return (support, sliding) if phase < 8 else (sliding, support)


def walking_feet(step_index: float) -> tuple[MoonwalkFoot, MoonwalkFoot]:
    """Walk forward with a planted stance foot and a raised returning foot."""
    phase = step_index % 8
    progress = (phase % 4) / 4
    support = MoonwalkFoot(7 - 14 * progress, 0)
    swing = MoonwalkFoot(-7 + 14 * progress, 0, 9 * sin(pi * progress))
    return (support, swing) if phase < 4 else (swing, support)


def draw_moonwalker(
    draw: ImageDraw.ImageDraw,
    center_x: int,
    center_y: int,
    *,
    pose: str = "moonwalk",
    step_index: float = 0,
    facing: int = 1,
) -> None:
    """Draw the reference outfit in pixel art, facing opposite its travel."""
    if pose in ("moonwalk", "walk"):
        _draw_moonwalk_profile(draw, center_x, center_y, step_index, facing, walking=pose == "walk")
        return

    suit = "#d9d7ba"
    light = "#f4efd6"
    shade = "#939583"
    outline = "#555d61"
    blue = "#596d91"
    blue_light = "#8999b1"
    shoes = "#242b39"

    def polygon(points: tuple[tuple[float, float], ...], color: str) -> None:
        draw.polygon([(center_x + facing * round(x), center_y + round(y)) for x, y in points], fill=color)

    def line(points: tuple[tuple[float, float], ...], color: str, width: int = 2) -> None:
        draw.line([(center_x + facing * round(x), center_y + round(y)) for x, y in points], fill=color, width=width)

    draw.ellipse((center_x - 25, center_y + 36, center_x + 25, center_y + 40), fill=COLORS["performer_shadow"])
    feet = (MoonwalkFoot(-10, 0), MoonwalkFoot(9, 9 if pose == "final" else 0))
    for index, foot in enumerate(feet):
        hip = -4 if index == 0 else 4
        ankle_y = 29 if foot.raised_heel else 34
        knee = (hip + foot.x) // 2
        if pose == "kick" and index == 1:
            ankle_y, knee = 8, 15
            foot = MoonwalkFoot(25, False)
        elif pose == "turn":
            knee += 4 if index else -4
        polygon(
            ((hip - 5, 0), (hip + 5, 0), (knee + 4, 18), (foot.x + 4, ankle_y), (foot.x - 4, ankle_y), (knee - 4, 18)),
            outline,
        )
        line(((hip, 3), (knee, 18), (foot.x, ankle_y)), suit, 7)
        line(((hip - 2, 5), (knee - 2, 18), (foot.x - 2, ankle_y - 2)), light, 2)
        line(((foot.x - 3, ankle_y), (foot.x + 3, ankle_y)), blue_light, 3)
        if foot.raised_heel:
            polygon(
                (
                    (foot.x - 4, 29),
                    (foot.x + 1, 29),
                    (foot.x + 7, 34),
                    (foot.x + 7, 36),
                    (foot.x + 3, 36),
                    (foot.x - 4, 32),
                ),
                shoes,
            )
            line(((foot.x + 3, 36), (foot.x + 7, 36)), light, 1)
        else:
            polygon(
                (
                    (foot.x - 4, ankle_y),
                    (foot.x + 2, ankle_y),
                    (foot.x + 7, ankle_y + 1),
                    (foot.x + 8, ankle_y + 3),
                    (foot.x - 4, ankle_y + 3),
                ),
                shoes,
            )
            line(((foot.x - 4, ankle_y + 3), (foot.x + 8, ankle_y + 3)), shade, 1)

    # Stepped silhouettes and three shades retain the reference's cream suit.
    polygon(((-14, -23), (-9, -28), (5, -26), (12, -20), (12, 2), (6, 8), (-2, 4), (-9, 7), (-13, -5)), outline)
    polygon(((-12, -22), (-7, -26), (4, -24), (10, -19), (9, 1), (5, 5), (-2, 2), (-8, 5), (-11, -5)), suit)
    polygon(((-3, -24), (4, -23), (5, -3), (0, 1), (-3, -6)), blue)
    line(((1, -21), (2, -4)), blue_light, 2)
    polygon(((-8, -25), (-3, -25), (0, -17), (-5, -19), (-3, -3), (-7, 0)), light)
    polygon(((4, -24), (7, -22), (6, -15), (3, -17)), light)
    line(((-10, -4), (-10, 2), (-6, 3)), shade)
    line(((7, -6), (6, 1)), shade)
    left_hand, right_hand = (-8, -1), (12, -5)
    if pose == "point":
        right_hand = (25, -29)
    elif pose == "final":
        right_hand = (7, -36)
    elif pose == "kick":
        left_hand = (-20, -19)
    elif pose == "turn":
        left_hand, right_hand = (-21, -12), (20, -14)
    line(((-10, -21), (-15, -11), left_hand), outline, 9)
    line(((-10, -21), (-15, -11), left_hand), suit, 6)
    line(((-11, -21), (-16, -11)), light, 2)
    line(((8, -20), (14, -12), right_hand), shade, 8)
    line(((8, -20), (14, -12), right_hand), suit, 5)
    line(((left_hand[0] - 2, left_hand[1]), (left_hand[0] + 2, left_hand[1])), light, 4)
    line(((right_hand[0] - 2, right_hand[1]), (right_hand[0] + 2, right_hand[1])), light, 4)

    # Face tucked beneath the fedora; brim, blue band and pale crown stay fixed.
    polygon(((-6, -34), (5, -34), (7, -31), (4, -27), (-3, -27), (-6, -30)), shade)
    polygon(((0, -33), (5, -33), (7, -31), (4, -29), (0, -29)), light)
    polygon(
        (
            (-14, -35),
            (-10, -37),
            (-9, -44),
            (-4, -46),
            (0, -43),
            (5, -45),
            (8, -41),
            (8, -36),
            (12, -34),
            (12, -32),
            (-12, -32),
        ),
        outline,
    )
    polygon(
        ((-12, -35), (-8, -36), (-7, -43), (-4, -44), (0, -41), (5, -43), (6, -40), (6, -35), (10, -34), (-11, -33)),
        suit,
    )
    line(((-7, -42), (-4, -39), (1, -39), (5, -42)), light, 2)
    line(((-7, -36), (6, -36)), blue, 2)
    line(((-11, -33), (10, -33)), light, 1)


def _draw_moonwalk_profile(
    draw: ImageDraw.ImageDraw,
    center_x: int,
    center_y: int,
    step_index: float,
    facing: int,
    *,
    walking: bool = False,
) -> None:
    """Draw a lateral backslide with toe pivots and a bent support knee."""
    outline = "#555d61"
    suit = "#d9d7ba"
    light = "#f4efd6"
    shade = "#939583"
    blue = "#596d91"

    def polygon(points: tuple[tuple[float, float], ...], color: str) -> None:
        draw.polygon([(center_x + facing * round(x), center_y + round(y)) for x, y in points], fill=color)

    def line(points: tuple[tuple[float, float], ...], color: str, width: int = 2) -> None:
        draw.line([(center_x + facing * round(x), center_y + round(y)) for x, y in points], fill=color, width=width)

    draw.ellipse((center_x - 26, center_y + 37, center_x + 23, center_y + 40), fill=COLORS["performer_shadow"])
    feet = walking_feet(step_index) if walking else moonwalk_feet(step_index)
    for index, foot in enumerate(feet):
        # Foot.x is the toe contact, not the ankle: lifting a heel cannot move it.
        heel_x = foot.x - 12 + foot.heel_lift * 0.55
        ankle_x = heel_x + 2
        ankle_y = 34 - foot.heel_lift - foot.toe_lift
        bend = foot.heel_lift / 9
        knee_x = ankle_x / 2 + bend * 7
        knee_y = 18 - bend * 4 - foot.toe_lift * 0.5
        leg_color = shade if index == 0 else suit
        polygon(
            (
                (-5, 0),
                (4, 0),
                (knee_x + 4, knee_y),
                (ankle_x + 4, ankle_y),
                (ankle_x - 4, ankle_y),
                (knee_x - 4, knee_y),
            ),
            outline,
        )
        line(((0, 3), (knee_x, knee_y), (ankle_x, ankle_y - 1)), leg_color, 7)
        line(((-2, 4), (knee_x - 2, knee_y), (ankle_x - 2, ankle_y - 2)), light if index else suit, 2)
        line(((ankle_x - 3, ankle_y), (ankle_x + 3, ankle_y)), "#c6d0d6", 3)
        polygon(
            (
                (heel_x, 36 - foot.heel_lift - foot.toe_lift),
                (heel_x + 1, 32 - foot.heel_lift - foot.toe_lift),
                (heel_x + 5, 32 - foot.heel_lift - foot.toe_lift),
                (foot.x - 1, 34 - foot.toe_lift),
                (foot.x + 2, 35 - foot.toe_lift),
                (foot.x + 2, 37 - foot.toe_lift),
                (foot.x - 1, 37 - foot.toe_lift),
            ),
            "#242b39",
        )
        line(
            (
                (heel_x, 36 - foot.heel_lift - foot.toe_lift),
                (foot.x - 1, 37 - foot.toe_lift),
                (foot.x + 2, 37 - foot.toe_lift),
            ),
            shade,
            1,
        )

    # One narrow shoulder and overlapping arms make the body read in profile.
    polygon(((-9, -23), (-5, -27), (5, -27), (11, -22), (10, -8), (7, 3), (2, 7), (-6, 5), (-10, -5)), outline)
    polygon(((-7, -23), (-3, -25), (4, -25), (8, -21), (8, -8), (5, 2), (1, 5), (-5, 3), (-8, -6)), suit)
    polygon(((5, -25), (9, -21), (8, -4), (5, 0), (3, -7)), blue)
    line(((7, -21), (6, -5)), "#8999b1", 2)
    polygon(((-2, -25), (3, -26), (6, -21), (3, -15), (0, -17), (1, -4), (-3, 2)), light)
    line(((-6, -5), (-5, 1), (-2, 2)), shade, 2)
    # Far hand sits at the belt; near arm trails with a relaxed elbow.
    line(((7, -21), (12, -10), (6, -1)), shade, 6)
    line(((6, -1), (9, -1)), light, 3)
    line(((-4, -22), (-9, -12), (-9, -6), (-3, 0)), outline, 8)
    line(((-4, -22), (-9, -12), (-9, -6), (-3, 0)), suit, 5)
    line(((-5, -21), (-10, -12)), light, 2)
    line(((-4, -1), (-1, 1)), light, 4)

    # Nose, chin and forward brim establish an unambiguous facing direction.
    polygon(((-2, -35), (8, -35), (9, -32), (12, -31), (9, -29), (8, -26), (3, -26), (1, -28), (-2, -29)), outline)
    polygon(((3, -34), (8, -34), (8, -32), (11, -31), (8, -30), (7, -27), (4, -27), (2, -30)), light)
    polygon(
        (
            (-10, -35),
            (-6, -37),
            (-5, -43),
            (-2, -45),
            (2, -42),
            (6, -43),
            (9, -40),
            (9, -36),
            (15, -34),
            (15, -32),
            (-9, -32),
        ),
        outline,
    )
    polygon(
        ((-8, -35), (-4, -36), (-3, -42), (-1, -43), (2, -40), (6, -41), (7, -39), (7, -35), (12, -34), (-7, -33)), suit
    )
    line(((-3, -41), (0, -39), (4, -39), (6, -40)), light, 2)
    line(((-4, -36), (8, -36)), blue, 2)
    line(((-8, -33), (13, -33)), light, 1)


def _level_color(contribution: ContributionDay) -> str:
    if contribution.count == 0:
        return COLORS["grid_base"]
    return COLORS.get(contribution.level, COLORS["grid_base"])


def _performer_anchor(calendar: ContributionCalendar, layout: GridLayout) -> tuple[int, int]:
    last_week_index = len(calendar.weeks) - 1
    last_day = calendar.days[-1]
    weekday = (last_day.day.weekday() + 1) % 7
    return layout.cell_center(last_week_index, weekday)


def _draw_stars(draw: ImageDraw.ImageDraw, width: int, height: int) -> None:
    for index in range(18):
        x = (index * 137 + 29) % width
        y = (index * 47 + 11) % max(1, height - GRID_BOTTOM)
        if y < GRID_TOP - 8:
            draw.point((x, y), fill=COLORS["star"])
