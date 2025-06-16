import click

@click.group()
def cli():
    """
    A command-line tool for managing your Advent of Code environment.
    """
    pass

@cli.command()
def hello():
    """Prints a friendly greeting."""
    click.echo("👋 Hello! Your AoC environment is set up correctly.")

if __name__ == "__main__":
    cli()
