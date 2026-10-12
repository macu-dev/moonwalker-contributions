"""Persist generated animation assets without partial image files."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from tempfile import NamedTemporaryFile

from PIL import Image

from moonwalk_contributions.animation import AnimationSequence

MAX_GIF_SIZE_BYTES = 3_000_000
MAX_PALETTE_SOURCE_COLORS = 1_000_000


@dataclass(frozen=True)
class GeneratedAssets:
    """Paths to the animated and static generated resources."""

    animation: Path
    fallback: Path


def save_animation(sequence: AnimationSequence, output_dir: Path) -> GeneratedAssets:
    """Write an optimized looping GIF and a static PNG fallback."""
    if not sequence.frames:
        raise ValueError("Cannot save an animation without frames.")
    if len(sequence.frames) != len(sequence.durations_ms):
        raise ValueError("Every animation frame must have a playback duration.")

    output_dir.mkdir(parents=True, exist_ok=True)
    animation_path = output_dir / "moonwalk-contributions.gif"
    fallback_path = output_dir / "moonwalk-contributions.png"

    temporary_paths: list[Path] = []
    try:
        temporary_animation = _temporary_path(output_dir, ".gif")
        temporary_paths.append(temporary_animation)
        temporary_fallback = _temporary_path(output_dir, ".png")
        temporary_paths.append(temporary_fallback)
        images = [frame.image for frame in sequence.frames]
        palette = _shared_palette(images)
        gif_frames = [image.quantize(palette=palette, dither=Image.Dither.NONE) for image in images]
        gif_frames[0].save(
            temporary_animation,
            format="GIF",
            save_all=True,
            append_images=gif_frames[1:],
            duration=list(sequence.durations_ms),
            loop=0,
            optimize=True,
            disposal=1,
        )
        sequence.frames[-1].image.save(temporary_fallback, format="PNG", optimize=True)

        if temporary_animation.stat().st_size > MAX_GIF_SIZE_BYTES:
            raise ValueError(f"Generated GIF is larger than the {MAX_GIF_SIZE_BYTES // 1_000_000} MB size limit.")
        os.replace(temporary_animation, animation_path)
        os.replace(temporary_fallback, fallback_path)
    finally:
        for temporary_path in temporary_paths:
            temporary_path.unlink(missing_ok=True)

    return GeneratedAssets(animation=animation_path, fallback=fallback_path)


def _temporary_path(output_dir: Path, suffix: str) -> Path:
    with NamedTemporaryFile(prefix=".moonwalk-", suffix=suffix, dir=output_dir, delete=False) as temporary_file:
        return Path(temporary_file.name)


def _shared_palette(images: list[Image.Image]) -> Image.Image:
    """Build one stable palette from every frame so GIF deltas compress well."""
    colors: set[tuple[int, int, int]] = set()
    for image in images:
        frame_colors = image.getcolors(maxcolors=MAX_PALETTE_SOURCE_COLORS)
        if frame_colors is None:
            raise ValueError("Animation frame has too many colors to build a shared GIF palette.")
        for _, color in frame_colors:
            if not isinstance(color, tuple) or len(color) != 3:
                raise ValueError("Animation frames must use RGB colors to build a shared GIF palette.")
            colors.add((color[0], color[1], color[2]))

    palette_source = Image.new("RGB", (len(colors), 1))
    palette_source.putdata(sorted(colors))
    return palette_source.quantize(colors=256, method=Image.Quantize.MEDIANCUT)
