import os
import configparser
import click
from .constants import MAIN_CONTENTS, GITIGNORE_CONTENTS


def create_default_config(path, cookies):
    config = configparser.ConfigParser()
    config["settings"] = {
        "bind_on_correct": "True",
        "clear_on_bind": "False",
        "commit_on_bind": "False",
        "auto_bump_on_correct": "False",
    }
    config["variables"] = {
        "path": path,
        "session_cookies": cookies,
        "default_year": "2025",
        "default_day": "1",
        "default_part": "1",
    }
    return config


def get_config():
    config_path = "config.toml"

    assert os.path.exists(config_path)

    with open(config_path, "r") as f:
        config = configparser.ConfigParser()
        config.read_file(f)

    return config


def write_config(config: configparser.ConfigParser):
    config_path = "config.toml"
    with open(config_path, "w") as f:
        config.write(f)


def get_session_cookies():
    config = get_config()
    cookies = dict()
    cookies["session"] = config["variables"]["session_cookies"]
    return cookies


def build_environment(path, config):
    files = [".gitignore", "main.py", "config.toml"]
    directories = [".aoc", ".aoc/cache", "solutions"]

    for dir in directories:
        p = os.path.join(path, dir)
        if not os.path.isdir(p):
            os.mkdir(p)

    for file in files:
        p = os.path.join(path, file)
        with open(p, "w") as f:
            if "main.py" in p:
                f.write(
                    MAIN_CONTENTS.format(
                        year=config.get("variables", "default_year"),
                        day=config.get("variables", "default_day"),
                        part=config.get("variables", "default_part"),
                    )
                )
            elif ".gitignore" in p:
                f.write(GITIGNORE_CONTENTS)
            else:
                f.write("")


def run_wizard(config):
    config["variables"] = {
        "path": config["variables"]["path"],
        "session_cookies": click.prompt(
            "Please paste your session cookies. (Instructions in README.md)", type=str
        ),
        "default_year": click.prompt("Default year", type=int),
        "default_day": click.prompt("Default day", type=int),
        "default_part": click.prompt("Default part", type=int),
    }
    config["settings"] = {
        "bind_on_correct": str(
            click.confirm(
                "Do you want the solution to bind when you submit correct solution?",
                True,
            )
        ),
        "clear_on_bind": str(
            click.confirm(
                "Do you want to main.py to be cleared when you bind the soution?"
            )
        ),
        "commit_on_bind": str(
            click.confirm(
                "Do you want to commit your solution when you bind the solution?"
            )
        ),
        "auto_bump_on_correct": str(
            click.confirm(
                "Do you want to automatically bump to the next puzzle on a correct submission?"
            )
        ),
    }
    return config
