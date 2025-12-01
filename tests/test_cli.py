import os
import configparser
from click.testing import CliRunner
from aoc.cli import cli, init, run, context



def test_cli_group():
    """Test the main CLI group."""
    runner = CliRunner()
    result = runner.invoke(cli, ["--help"])
    assert result.exit_code == 0
    assert "A CLI tool for aocenv" in result.output


def test_context_command_display(tmp_path):
    """Test context command displays default context."""
    runner = CliRunner()
    with runner.isolated_filesystem(temp_dir=tmp_path):
        # Initialize a project
        runner.invoke(init, [".", "--default"])

        result = runner.invoke(context)
        assert result.exit_code == 0
        assert "Default context: year=2025, day=1, part=1" in result.output


def test_context_command_set_all(tmp_path):
    """Test context command sets all context values."""
    runner = CliRunner()
    with runner.isolated_filesystem(temp_dir=tmp_path):
        runner.invoke(init, [".", "--default"])

        result = runner.invoke(context, ["--year", "2025", "--day", "10", "--part", "2"])
        assert result.exit_code == 0
        assert "Default context set to: year=2025, day=10, part=2" in result.output

        # Verify change in config
        config = configparser.ConfigParser()
        config.read("config.toml")
        assert config.get("variables", "default_year") == "2025"
        assert config.get("variables", "default_day") == "10"
        assert config.get("variables", "default_part") == "2"


def test_context_command_set_partial(tmp_path):
    """Test context command sets partial context values."""
    runner = CliRunner()
    with runner.isolated_filesystem(temp_dir=tmp_path):
        runner.invoke(init, [".", "--default"])

        # Set only year
        result = runner.invoke(context, ["--year", "2026"])
        assert result.exit_code == 0
        assert "Default context set to: year=2026, day=1, part=1" in result.output

        # Set day and part
        result = runner.invoke(context, ["--day", "15", "--part", "1"])
        assert result.exit_code == 0
        assert "Default context set to: year=2026, day=15, part=1" in result.output

        # Verify change in config
        config = configparser.ConfigParser()
        config.read("config.toml")
        assert config.get("variables", "default_year") == "2026"
        assert config.get("variables", "default_day") == "15"
        assert config.get("variables", "default_part") == "1"




def test_init_command(tmp_path):
    runner = CliRunner()
    result = runner.invoke(init, [str(tmp_path), "--default"])
    assert result.exit_code == 0

    # Check that the directories were created
    assert os.path.isdir(os.path.join(tmp_path, ".aoc"))
    assert os.path.isdir(os.path.join(tmp_path, ".aoc/cache"))
    assert os.path.isdir(os.path.join(tmp_path, "solutions"))

    # Check that the files were created
    main_py_path = os.path.join(tmp_path, "main.py")
    config_toml_path = os.path.join(tmp_path, "config.toml")
    assert os.path.isfile(main_py_path)
    assert os.path.isfile(config_toml_path)

    # Check the contents of main.py
    with open(main_py_path, "r") as f:
        content = f.read()
        assert "YEAR, DAY, PART = (2025, 1, 1)" in content

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
    result = runner.invoke(
        init, [str(tmp_path)], input="test_session\n2025\n1\n1\ny\nn\ny\n"
    )
    assert result.exit_code == 0

    # Check that config was created with wizard inputs
    config_toml_path = os.path.join(tmp_path, "config.toml")
    config = configparser.ConfigParser()
    config.read(config_toml_path)
    assert config["variables"]["session_cookies"] == "test_session"
    assert config.get("variables", "default_year") == "2025"
    assert config.get("variables", "default_day") == "1"
    assert config.get("variables", "default_part") == "1"


def test_run_command():
    """Test the run command."""
    runner = CliRunner()
    result = runner.invoke(run)
    assert result.exit_code == 0
