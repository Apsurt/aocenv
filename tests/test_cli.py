import os
import configparser
from click.testing import CliRunner
from aoc.cli import cli, init, run
from aoc.cli import test as cli_test
from aoc.constants import MAIN_CONTENTS

def test_cli_group():
    """Test the main CLI group."""
    runner = CliRunner()
    result = runner.invoke(cli, ["--help"])
    assert result.exit_code == 0
    assert "A CLI tool for aocenv" in result.output

def test_init_command(tmp_path):
    runner = CliRunner()
    result = runner.invoke(init, [str(tmp_path), "--default"])
    assert result.exit_code == 0

    # Check that the directories were created
    assert os.path.isdir(os.path.join(tmp_path, ".aoc"))
    assert os.path.isdir(os.path.join(tmp_path, ".aoc/.cache"))
    assert os.path.isdir(os.path.join(tmp_path, "solutions"))
    assert os.path.isdir(os.path.join(tmp_path, ".aoc/.cache/inputs"))

    # Check that the files were created
    main_py_path = os.path.join(tmp_path, "main.py")
    config_toml_path = os.path.join(tmp_path, "config.toml")
    assert os.path.isfile(main_py_path)
    assert os.path.isfile(config_toml_path)

    # Check the contents of main.py
    with open(main_py_path, "r") as f:
        assert f.read() == MAIN_CONTENTS

    # Check the contents of config.toml
    config = configparser.ConfigParser()
    config.read(config_toml_path)
    assert config["settings"]["bind_on_correct"] == "True"
    assert config["settings"]["clear_on_bind"] == "False"
    assert config["settings"]["commit_on_bind"] == "False"
    assert config["variables"]["path"] == str(tmp_path)
    assert config["variables"]["session_cookies"] == ""

def test_init_with_relative_path(tmp_path):
    """Test init command with relative path."""
    runner = CliRunner()
    # Use a relative path
    relative_path = "test_project"

    with runner.isolated_filesystem(temp_dir=tmp_path):
        result = runner.invoke(init, [relative_path, "--default"])
        assert result.exit_code == 0
        # Check that the directory was created and exists
        assert os.path.isdir(relative_path)

def test_init_creates_directory_if_not_exists(tmp_path):
    """Test init command creates directory if it doesn't exist."""
    runner = CliRunner()
    new_dir = os.path.join(tmp_path, "new_project")

    result = runner.invoke(init, [new_dir, "--default"])
    assert result.exit_code == 0
    assert os.path.isdir(new_dir)

def test_init_with_wizard(tmp_path):
    """Test init command with wizard (non-default mode)."""
    runner = CliRunner()
    # Simulate user input for the wizard
    result = runner.invoke(init, [str(tmp_path)], input="test_session\ny\nn\ny\n")
    assert result.exit_code == 0

    # Check that config was created with wizard inputs
    config_toml_path = os.path.join(tmp_path, "config.toml")
    config = configparser.ConfigParser()
    config.read(config_toml_path)
    assert config["variables"]["session_cookies"] == "test_session"

def test_run_command():
    """Test the run command."""
    runner = CliRunner()
    result = runner.invoke(run)
    assert result.exit_code == 0

def test_test_command():
    """Test the test command."""
    runner = CliRunner()
    result = runner.invoke(cli_test)
    assert result.exit_code == 0
