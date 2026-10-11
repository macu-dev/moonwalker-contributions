"""Command-line interface for the contribution animation generator."""

from __future__ import annotations

import argparse
import os
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path

from moonwalk_contributions import __version__
from moonwalk_contributions.github import GitHubAPIError
from moonwalk_contributions.pipeline import generate_contribution_assets


@dataclass(frozen=True)
class CLIOptions:
    """User-provided settings for one generator run."""

    username: str
    output_dir: Path


def build_parser() -> argparse.ArgumentParser:
    """Build the command-line argument parser."""
    parser = argparse.ArgumentParser(
        prog="moonwalk-contributions",
        description="Generate a moonwalk animation from a GitHub contribution calendar.",
    )
    parser.add_argument("--version", action="version", version=__version__)
    parser.add_argument(
        "--username",
        required=True,
        help="GitHub account whose contribution calendar will be rendered.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("assets"),
        help="Directory for generated images (default: assets).",
    )
    return parser


def parse_args(arguments: Sequence[str] | None = None) -> CLIOptions:
    """Parse command-line options for a generator run."""
    parsed = build_parser().parse_args(arguments)
    return CLIOptions(username=parsed.username, output_dir=parsed.output_dir)


def get_github_token(environ: Mapping[str, str] | None = None) -> str | None:
    """Read the optional API token from the process environment."""
    environment = os.environ if environ is None else environ
    return environment.get("GITHUB_TOKEN")


def main(arguments: Sequence[str] | None = None) -> int:
    """Run the command-line interface."""
    options = parse_args(arguments)
    try:
        generate_contribution_assets(options.username, get_github_token(), options.output_dir)
    except (GitHubAPIError, OSError, ValueError) as error:
        build_parser().error(str(error))
    return 0
