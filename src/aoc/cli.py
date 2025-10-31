import os
from typing_extensions import Optional
import click
from .configuration import create_default_config, run_wizard, build_environment
from .run import run_main
from .bind import run_bind

@click.group()
def cli():
    """A CLI tool for aocenv."""
    pass

@cli.command()
@click.argument("path", required=True)
@click.argument("session_cookies", required=False)
@click.option("--default", is_flag=True)
def init(path: str, session_cookies: Optional[str], default: bool):
    """Runs configuration the wizard"""

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
    #TODO Add timing flag
    run_main()

@cli.command()
@click.argument("name", required=False)
@click.option("--force", is_flag=True, required=False, default=False)
def bind(name: Optional[str], force: bool):
    """Binds the contents of main.py"""
    run_bind(name, force)

@cli.command()
@click.argument("year", required=True)
@click.argument("day", required=True)
@click.argument("part", required=True)
@click.argument("name", required=False)
def load(year: int, day: int, part: int, name: str):
    """Loads saved solution into main.py"""
    #TODO

    pass

@cli.command()
def test():
    """TBA"""
    #TODO in v0.2.0
    pass

if __name__ == "__main__":
    cli()
