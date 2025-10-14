import click
from aoc import example_function

@click.group()
def cli():
    """A CLI tool for aocenv."""
    pass

@cli.command()
def hello():
    """Prints a hello message."""
    click.echo(example_function())

if __name__ == "__main__":
    cli()
