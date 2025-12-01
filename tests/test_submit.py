import pytest
from unittest.mock import patch, Mock
import os
import configparser

from aoc.context import Context
from aoc.submit import submit
from aoc.configuration import create_default_config, write_config


@pytest.fixture
def mock_project_root(tmp_path):
    """Fixture to set up a temporary project environment."""
    (tmp_path / "main.py").touch()
    (tmp_path / "config.toml").touch()

    config = create_default_config(str(tmp_path), "test_session_id")
    write_config(config)

    old_cwd = os.getcwd()
    os.chdir(tmp_path)
    yield tmp_path
    os.chdir(old_cwd)


@patch("requests.post")
@patch("aoc.submit.get_context")
@patch("aoc.submit.get_config")
@patch("aoc.submit.write_config")
@patch("aoc.submit.run_bind")
@patch("aoc.submit.get_session_cookies")
def test_submit_correct_no_autobump(
    mock_get_session_cookies,
    mock_run_bind,
    mock_write_config,
    mock_get_config,
    mock_get_context,
    mock_post,
    mock_project_root,
):
    """Test correct submission when auto_bump is disabled."""
    # Arrange
    ctx = Context(year=2025, day=1, part=1)
    mock_get_context.return_value = ctx
    mock_get_session_cookies.return_value = {"session": "mock_session_id"}

    mock_config = configparser.ConfigParser()
    mock_config["settings"] = {
        "auto_bump_on_correct": "False",
        "bind_on_correct": "False",
    }
    mock_config["variables"] = {
        "session_cookies": "mock_session_id",
        "default_year": "2025",
        "default_day": "1",
        "default_part": "1",
    }
    mock_get_config.return_value = mock_config

    mock_post_response = Mock()
    mock_post_response.status_code = 200
    mock_post_response.text = "<article>That's the right answer!</article>"
    mock_post_response.raise_for_status.return_value = None
    mock_post.return_value = mock_post_response

    # Act
    submit(123)

    # Assert
    mock_post.assert_called_once()
    mock_write_config.assert_not_called()
    mock_run_bind.assert_not_called()


@patch("requests.post")
@patch("aoc.submit.get_context")
@patch("aoc.submit.get_config")
@patch("aoc.submit.write_config")
@patch("aoc.submit.run_bind")
@patch("aoc.submit.get_session_cookies")
def test_submit_correct_with_bind_on_correct(
    mock_get_session_cookies,
    mock_run_bind,
    mock_write_config,
    mock_get_config,
    mock_get_context,
    mock_post,
    mock_project_root,
):
    """Test correct submission with bind_on_correct enabled."""
    # Arrange
    ctx = Context(year=2025, day=1, part=1)
    mock_get_context.return_value = ctx
    mock_get_session_cookies.return_value = {"session": "mock_session_id"}

    mock_config = configparser.ConfigParser()
    mock_config["settings"] = {
        "auto_bump_on_correct": "False",
        "bind_on_correct": "True",
    }
    mock_config["variables"] = {
        "session_cookies": "mock_session_id",
        "default_year": "2025",
        "default_day": "1",
        "default_part": "1",
    }
    mock_get_config.return_value = mock_config

    mock_post_response = Mock()
    mock_post_response.status_code = 200
    mock_post_response.text = "<article>That's the right answer!</article>"
    mock_post_response.raise_for_status.return_value = None
    mock_post.return_value = mock_post_response

    # Act
    submit(123)

    # Assert
    mock_post.assert_called_once()
    mock_write_config.assert_not_called()
    mock_run_bind.assert_called_once()


@patch("requests.post")
@patch("aoc.submit.get_context")
@patch("aoc.submit.get_config")
@patch("aoc.submit.write_config")
@patch("aoc.submit.run_bind")
@patch("aoc.submit.get_session_cookies")
def test_submit_correct_autobump_part1_to_part2(
    mock_get_session_cookies,
    mock_run_bind,
    mock_write_config,
    mock_get_config,
    mock_get_context,
    mock_post,
    mock_project_root,
):
    """Test auto_bump from Part 1 to Part 2."""
    # Arrange
    ctx = Context(year=2025, day=1, part=1)
    mock_get_context.return_value = ctx
    mock_get_session_cookies.return_value = {"session": "mock_session_id"}

    mock_config = configparser.ConfigParser()
    mock_config["settings"] = {
        "auto_bump_on_correct": "True",
        "bind_on_correct": "False",
    }
    mock_config["variables"] = {
        "session_cookies": "mock_session_id",
        "default_year": "2025",
        "default_day": "1",
        "default_part": "1",
    }
    mock_get_config.return_value = mock_config

    mock_post_response = Mock()
    mock_post_response.status_code = 200
    mock_post_response.text = "<article>That's the right answer!</article>"
    mock_post_response.raise_for_status.return_value = None
    mock_post.return_value = mock_post_response

    # Act
    submit(123)

    # Assert
    mock_post.assert_called_once()
    mock_write_config.assert_called_once()
    mock_run_bind.assert_not_called()

    updated_config = mock_get_config.return_value
    assert updated_config.get("variables", "default_year") == "2025"
    assert updated_config.get("variables", "default_day") == "1"
    assert updated_config.get("variables", "default_part") == "2"


@patch("requests.post")
@patch("aoc.submit.get_context")
@patch("aoc.submit.get_config")
@patch("aoc.submit.write_config")
@patch("aoc.submit.run_bind")
@patch("aoc.submit.get_session_cookies")
def test_submit_correct_autobump_part2_to_next_day(
    mock_get_session_cookies,
    mock_run_bind,
    mock_write_config,
    mock_get_config,
    mock_get_context,
    mock_post,
    mock_project_root,
):
    """Test auto_bump from Part 2 to next day (Part 1)."""
    # Arrange
    ctx = Context(year=2025, day=1, part=2)
    mock_get_context.return_value = ctx
    mock_get_session_cookies.return_value = {"session": "mock_session_id"}

    mock_config = configparser.ConfigParser()
    mock_config["settings"] = {
        "auto_bump_on_correct": "True",
        "bind_on_correct": "False",
    }
    mock_config["variables"] = {
        "session_cookies": "mock_session_id",
        "default_year": "2025",
        "default_day": "1",
        "default_part": "2",
    }
    mock_get_config.return_value = mock_config

    mock_post_response = Mock()
    mock_post_response.status_code = 200
    mock_post_response.text = "<article>That's the right answer!</article>"
    mock_post_response.raise_for_status.return_value = None
    mock_post.return_value = mock_post_response

    # Act
    submit(123)

    # Assert
    mock_post.assert_called_once()
    mock_write_config.assert_called_once()
    mock_run_bind.assert_not_called()

    updated_config = mock_get_config.return_value
    assert updated_config.get("variables", "default_year") == "2025"
    assert updated_config.get("variables", "default_day") == "2"
    assert updated_config.get("variables", "default_part") == "1"


@patch("requests.post")
@patch("aoc.submit.get_context")
@patch("aoc.submit.get_config")
@patch("aoc.submit.write_config")
@patch("aoc.submit.run_bind")
@patch("aoc.submit.get_session_cookies")
def test_submit_correct_autobump_day25_part2_to_next_year(
    mock_get_session_cookies,
    mock_run_bind,
    mock_write_config,
    mock_get_config,
    mock_get_context,
    mock_post,
    mock_project_root,
):
    """Test auto_bump from Day 25, Part 2 to next year (Day 1, Part 1)."""
    # Arrange
    ctx = Context(year=2025, day=25, part=2)
    mock_get_context.return_value = ctx
    mock_get_session_cookies.return_value = {"session": "mock_session_id"}

    mock_config = configparser.ConfigParser()
    mock_config["settings"] = {
        "auto_bump_on_correct": "True",
        "bind_on_correct": "False",
    }
    mock_config["variables"] = {
        "session_cookies": "mock_session_id",
        "default_year": "2025",
        "default_day": "25",
        "default_part": "2",
    }
    mock_get_config.return_value = mock_config

    mock_post_response = Mock()
    mock_post_response.status_code = 200
    mock_post_response.text = "<article>That's the right answer!</article>"
    mock_post_response.raise_for_status.return_value = None
    mock_post.return_value = mock_post_response

    # Act
    submit(123)

    # Assert
    mock_post.assert_called_once()
    mock_write_config.assert_called_once()
    mock_run_bind.assert_not_called()

    updated_config = mock_get_config.return_value
    assert updated_config.get("variables", "default_year") == "2026"
    assert updated_config.get("variables", "default_day") == "1"
    assert updated_config.get("variables", "default_part") == "1"


@patch("requests.post")
@patch("aoc.submit.get_context")
@patch("aoc.submit.get_config")
@patch("aoc.submit.write_config")
@patch("aoc.submit.run_bind")
@patch("aoc.submit.get_session_cookies")
def test_submit_wrong_autobump_not_triggered(
    mock_get_session_cookies,
    mock_run_bind,
    mock_write_config,
    mock_get_config,
    mock_get_context,
    mock_post,
    mock_project_root,
):
    """Test auto_bump is not triggered on wrong submission."""
    # Arrange
    ctx = Context(year=2025, day=1, part=1)
    mock_get_context.return_value = ctx
    mock_get_session_cookies.return_value = {"session": "mock_session_id"}

    mock_config = configparser.ConfigParser()
    mock_config["settings"] = {
        "auto_bump_on_correct": "True",
        "bind_on_correct": "True",
    }
    mock_config["variables"] = {
        "session_cookies": "mock_session_id",
        "default_year": "2025",
        "default_day": "1",
        "default_part": "1",
    }
    mock_get_config.return_value = mock_config

    mock_post_response = Mock()
    mock_post_response.status_code = 200
    mock_post_response.text = "<article>That's not the right answer!</article>"
    mock_post_response.raise_for_status.return_value = None
    mock_post.return_value = mock_post_response

    # Act
    submit(123)

    # Assert
    mock_post.assert_called_once()
    mock_write_config.assert_not_called()
    mock_run_bind.assert_not_called()
