import os
from typing import Optional
import click

from .configuration import (
    create_default_config,
    run_wizard,
    build_environment,
    get_config,
    write_config,
)
from .context import Context
from .run import run_main
from .bind import run_bind
from .load import run_load
from .clear import run_clear


@click.group()
def cli():
    """A CLI tool for aocenv."""
    pass


@cli.command()
@click.option("--year", type=int)
@click.option("--day", type=int)
@click.option("--part", type=int)
def context(year: Optional[int], day: Optional[int], part: Optional[int]):
    """Sets or displays the default context."""
    config = get_config()

    if year is None and day is None and part is None:
        # Display current default context
        default_year = config.get("variables", "default_year", fallback="2025")
        default_day = config.get("variables", "default_day", fallback="1")
        default_part = config.get("variables", "default_part", fallback="1")
        print(f"Default context: year={default_year}, day={default_day}, part={default_part}")
        return

    if year is not None:
        config.set("variables", "default_year", str(year))
    if day is not None:
        config.set("variables", "default_day", str(day))
    if part is not None:
        config.set("variables", "default_part", str(part))

    write_config(config)

    default_year = config.get("variables", "default_year")
    default_day = config.get("variables", "default_day")
    default_part = config.get("variables", "default_part")
    print(f"Default context set to: year={default_year}, day={default_day}, part={default_part}")


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

    build_environment(path, config)
    config_path = os.path.join(path, "config.toml")
    with open(config_path, "w") as configfile:
        config.write(configfile)


@cli.command()
def run():
    """Runs the main.py file"""
    # TODO Add timing flag
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
def load(year: int, day: int, part: int, name: Optional[str]):
    """Loads saved solution into main.py"""
    run_load(Context(year, day, part), name)


@cli.command()
def clear():
    """Sets the main.py contents to the default"""
    run_clear()


# @cli.command()
# def test():
#     """"""
#     #TODO in v0.2.0
#     pass

if __name__ == "__main__":
    cli()
