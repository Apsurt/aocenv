import os
import configparser
from click.testing import CliRunner
from aoc.cli import init
from aoc.constants import MAIN_CONTENTS

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
