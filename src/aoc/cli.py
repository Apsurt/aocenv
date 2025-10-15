import os
import click
from .configuration import create_default_config, get_config, run_wizard, build_environment

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
    if not os.path.exists(path):
        os.mkdir(path)

    config = create_default_config(path)

    if not default:
        config = run_wizard(config)

    build_environment(path)
    config_path = os.path.join(path, "config.toml")
    with open(config_path, "w") as configfile:
        config.write(configfile)

@cli.command()
def run():
    pass

@cli.command()
def test():
    pass

if __name__ == "__main__":
    cli()
