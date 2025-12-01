import pytest
from unittest.mock import patch, Mock
import os
import configparser
from pathlib import Path
import subprocess

from aoc.context import Context
from aoc.bind import run_bind
from aoc.configuration import create_default_config, write_config


@pytest.fixture
def mock_project_root_with_git(tmp_path):
    """Fixture to set up a temporary project environment with a Git repo."""
    (tmp_path / "main.py").write_text("print('Solution')")
    (tmp_path / "config.toml").touch()

    config = create_default_config(str(tmp_path), "test_session_id")
    config["settings"]["commit_on_bind"] = (
        "True"  # Default to True for tests that expect commit
    )
    write_config(config)

    old_cwd = os.getcwd()
    os.chdir(tmp_path)

    # Initialize Git repository
    subprocess.run(
        ["git", "init", "-b", "main"], capture_output=True, text=True, check=True
    )
    subprocess.run(
        ["git", "config", "user.email", "test@example.com"],
        capture_output=True,
        text=True,
        check=True,
    )
    subprocess.run(
        ["git", "config", "user.name", "Test User"],
        capture_output=True,
        text=True,
        check=True,
    )
    subprocess.run(
        ["git", "add", "main.py"], capture_output=True, text=True, check=True
    )
    subprocess.run(
        ["git", "commit", "-m", "Initial commit"],
        capture_output=True,
        text=True,
        check=True,
    )

    yield tmp_path
    os.chdir(old_cwd)


@patch("subprocess.run")
@patch("aoc.bind.get_context")
@patch("aoc.bind.get_config")
@patch("aoc.configuration.write_config")
def test_run_bind_commit_on_bind_disabled(
    mock_write_config,
    mock_get_config,
    mock_get_context,
    mock_subprocess_run,
    mock_project_root_with_git,
):
    """Test run_bind does not commit when commit_on_bind is disabled."""
    # Arrange
    ctx = Context(year=2025, day=1, part=1)
    mock_get_context.return_value = ctx

    mock_config = configparser.ConfigParser()
    mock_config["settings"] = {"commit_on_bind": "False", "clear_on_bind": "False"}
    mock_config["variables"] = {
        "path": str(mock_project_root_with_git),
        "session_cookies": "mock_session_id",
        "default_year": "2025",
        "default_day": "1",
        "default_part": "1",
    }
    mock_get_config.return_value = mock_config

    # Act
    run_bind(name=None, force=False)

    # Assert
    mock_subprocess_run.assert_not_called()
    mock_write_config.assert_not_called()  # config is not written by run_bind


@patch("subprocess.run")
@patch("aoc.bind.get_context")
@patch("aoc.bind.get_config")
@patch("aoc.configuration.write_config")
def test_run_bind_commit_on_bind_enabled_success(
    mock_write_config,
    mock_get_config,
    mock_get_context,
    mock_subprocess_run,
    mock_project_root_with_git,
):
    """Test run_bind commits when commit_on_bind is enabled."""
    # Arrange
    ctx = Context(year=2025, day=1, part=1)
    mock_get_context.return_value = ctx

    mock_config = configparser.ConfigParser()
    mock_config["settings"] = {"commit_on_bind": "True", "clear_on_bind": "False"}
    mock_config["variables"] = {
        "path": str(mock_project_root_with_git),
        "session_cookies": "mock_session_id",
        "default_year": "2025",
        "default_day": "1",
        "default_part": "1",
    }
    mock_get_config.return_value = mock_config

    # Mock subprocess.run for git commands
    mock_add_result = Mock()
    mock_add_result.returncode = 0
    mock_commit_result = Mock()
    mock_commit_result.returncode = 0

    # Configure side_effect for multiple calls
    mock_subprocess_run.side_effect = [
        mock_add_result,  # for git add
        mock_commit_result,  # for git commit
    ]

    # Act
    run_bind(name=None, force=False)

    # Assert
    # Assert git add was called
    bind_path = (
        Path(mock_project_root_with_git) / "solutions" / "2025" / "1" / "2025_1_1.py"
    )
    mock_subprocess_run.assert_any_call(
        ["git", "add", str(bind_path)], capture_output=True, text=True, check=False
    )
    # Assert git commit was called
    mock_subprocess_run.assert_any_call(
        ["git", "commit", "-m", "feat: Solve 2025 Day 1 Part 1"],
        capture_output=True,
        text=True,
        check=False,
    )
    assert mock_subprocess_run.call_count == 2
    mock_write_config.assert_not_called()
