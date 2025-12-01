"""Tests for configuration module."""

import os
import tempfile
import configparser
from unittest.mock import patch
from aoc.configuration import (
    create_default_config,
    get_config,
    get_session_cookies,
    build_environment,
    run_wizard,
    write_config,
)


def test_create_default_config():
    """Test creating default configuration."""
    config = create_default_config("/test/path", "test_cookie")

    assert config["settings"]["bind_on_correct"] == "True"
    assert config["settings"]["clear_on_bind"] == "False"
    assert config["settings"]["commit_on_bind"] == "False"
    assert config["settings"]["auto_bump_on_correct"] == "False"
    assert config["variables"]["path"] == "/test/path"
    assert config["variables"]["session_cookies"] == "test_cookie"
    assert config["variables"]["default_year"] == "2025"
    assert config["variables"]["default_day"] == "1"
    assert config.get("variables", "default_part") == "1"


def test_write_config():
    """Test writing configuration to file."""
    with tempfile.TemporaryDirectory() as tmpdir:
        old_cwd = os.getcwd()
        try:
            os.chdir(tmpdir)
            config = create_default_config("/test/path", "test_cookie")
            config.set("variables", "default_year", "2025")

            write_config(config)

            read_config = get_config()
            assert read_config.get("variables", "default_year") == "2025"
        finally:
            os.chdir(old_cwd)


def test_get_config():
    """Test reading configuration from file."""
    with tempfile.TemporaryDirectory() as tmpdir:
        old_cwd = os.getcwd()
        try:
            os.chdir(tmpdir)

            # Create a test config.toml
            config = configparser.ConfigParser()
            config["settings"] = {"bind_on_correct": "False"}
            config["variables"] = {"session_cookies": "test_session"}

            with open("config.toml", "w") as f:
                config.write(f)

            # Test get_config
            loaded_config = get_config()
            assert loaded_config["settings"]["bind_on_correct"] == "False"
            assert loaded_config["variables"]["session_cookies"] == "test_session"
        finally:
            os.chdir(old_cwd)


def test_get_config_missing_file():
    """Test get_config raises assertion error when file doesn't exist."""
    with tempfile.TemporaryDirectory() as tmpdir:
        old_cwd = os.getcwd()
        try:
            os.chdir(tmpdir)

            # No config.toml exists
            try:
                get_config()
                assert False, "Should have raised AssertionError"
            except AssertionError:
                pass  # Expected
        finally:
            os.chdir(old_cwd)


def test_get_session_cookies():
    """Test retrieving session cookies from config."""
    with tempfile.TemporaryDirectory() as tmpdir:
        old_cwd = os.getcwd()
        try:
            os.chdir(tmpdir)

            # Create a test config.toml
            config = configparser.ConfigParser()
            config["variables"] = {"session_cookies": "my_session_token"}

            with open("config.toml", "w") as f:
                config.write(f)

            # Test get_session_cookies
            cookies = get_session_cookies()
            assert cookies["session"] == "my_session_token"
        finally:
            os.chdir(old_cwd)


def test_build_environment():
    """Test building the project environment."""
    with tempfile.TemporaryDirectory() as tmpdir:
        config = create_default_config(tmpdir, "")
        build_environment(tmpdir, config)

        # Check directories
        assert os.path.isdir(os.path.join(tmpdir, ".aoc"))
        assert os.path.isdir(os.path.join(tmpdir, ".aoc/cache"))
        assert os.path.isdir(os.path.join(tmpdir, "solutions"))

        # Check files
        main_path = os.path.join(tmpdir, "main.py")
        config_path = os.path.join(tmpdir, "config.toml")
        assert os.path.isfile(main_path)
        assert os.path.isfile(config_path)

        # Check main.py content
        with open(main_path, "r") as f:
            content = f.read()
            assert "YEAR, DAY, PART = (2025, 1, 1)" in content

        # Check config.toml is empty
        with open(config_path, "r") as f:
            assert f.read() == ""


def test_build_environment_idempotent():
    """Test that build_environment can be run multiple times safely."""
    with tempfile.TemporaryDirectory() as tmpdir:
        config = create_default_config(tmpdir, "")
        # Run twice
        build_environment(tmpdir, config)
        build_environment(tmpdir, config)

        # Should still work
        assert os.path.isdir(os.path.join(tmpdir, ".aoc"))
        assert os.path.isfile(os.path.join(tmpdir, "main.py"))


def test_run_wizard():
    """Test the configuration wizard."""
    config = configparser.ConfigParser()
    config["variables"] = {"path": "/test/path"}
    config["settings"] = {}

    # Mock click.prompt and click.confirm
    with patch("click.prompt", side_effect=["wizard_session_token", 2025, 12, 2]):
        with patch("click.confirm", side_effect=[True, False, True, True]):
            result_config = run_wizard(config)

    # Check that wizard updated the config
    assert result_config["variables"]["session_cookies"] == "wizard_session_token"
    assert result_config["variables"]["path"] == "/test/path"
    assert result_config["variables"]["default_year"] == "2025"
    assert result_config["variables"]["default_day"] == "12"
    assert result_config["variables"]["default_part"] == "2"
    assert result_config["settings"]["bind_on_correct"] == "True"
    assert result_config["settings"]["clear_on_bind"] == "False"
    assert result_config["settings"]["commit_on_bind"] == "True"
    assert result_config["settings"]["auto_bump_on_correct"] == "True"
