import os
import click
import configparser
from .cli_commands import run_wizard, build_environment

@click.group()
def cli():
    """A CLI tool for aocenv."""
    pass

@cli.command()
@click.argument("path", required=False)
@click.option("--default", is_flag=True)
def init(path: str, default: bool):
    """Runs configuration the wizard."""

    base_path = os.getcwd()

    if path:
        path = os.path.join(base_path, path)
    else:
        path = base_path
    assert os.path.exists(path)

    build_environment(path)

    config = configparser.ConfigParser()
    config["settings"] = {}
    config["variables"] = {}

    if not default:
        config = run_wizard(config)
    else:
        config["settings"] = {
            "fav_color": "blue"
        }

        config["variables"] = {
            "path": path,
        }

    config_path = os.path.join(path, "config.toml")
    with open(config_path, 'w') as configfile:
        config.write(configfile)

if __name__ == "__main__":
    cli()
