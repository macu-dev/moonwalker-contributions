"""Tests for the public command-line interface."""

from pathlib import Path

import pytest

from moonwalk_contributions.cli import get_github_token, parse_args


def test_parse_args_accepts_target_username() -> None:
    """A user can select an account without editing project files."""
    options = parse_args(["--username", "octocat"])

    assert options.username == "octocat"
    assert options.output_dir == Path("assets")


def test_parse_args_accepts_output_directory() -> None:
    """A user can choose where generated assets are written."""
    options = parse_args(["--username", "octocat", "--output-dir", "build/images"])

    assert options.output_dir == Path("build/images")


def test_github_token_is_read_from_environment_only() -> None:
    """The API token is not part of command-line options."""
    token = "secret-token-value"

    assert get_github_token({"GITHUB_TOKEN": token}) == token
    assert "token" not in parse_args(["--username", "octocat"]).__dict__


def test_missing_github_token_is_reported_as_unconfigured() -> None:
    """Missing credentials are represented without exposing a value."""
    assert get_github_token({}) is None


def test_username_is_required() -> None:
    """A run cannot begin without a GitHub account."""
    with pytest.raises(SystemExit):
        parse_args([])
