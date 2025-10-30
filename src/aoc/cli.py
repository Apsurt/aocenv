import os
import click
from .configuration import create_default_config, run_wizard, build_environment
from .run import run_main

@click.group()
def cli():
    """A CLI tool for aocenv."""
    pass

@cli.command()
@click.argument("path", required=True)
@click.argument("session_cookies", required=False)
@click.option("--default", is_flag=True)
def init(path: str, session_cookies: str, default: bool):
    """Runs configuration the wizard."""

    if not os.path.isabs(path):
        path = os.path.abspath(path)

    if not os.path.exists(path):
        os.mkdir(path)

    if session_cookies is None:
        session_cookies = ""

    config = create_default_config(path, session_cookies)

    if not default:
        config = run_wizard(config)

    build_environment(path)
    config_path = os.path.join(path, "config.toml")
    with open(config_path, "w") as configfile:
        config.write(configfile)

@cli.command()
def run():
    """Runs the main.py file"""

    run_main()

@cli.command()
def test():
    pass

if __name__ == "__main__":
    cli()
