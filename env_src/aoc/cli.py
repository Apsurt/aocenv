import click
import configparser
from pathlib import Path

# Define the path to the config file within the env_src directory
# This assumes your cli.py is at env_src/aoc/cli.py
CONFIG_FILE_PATH = Path(__file__).parent.parent / "config.ini"

@click.group()
def cli():
    """
    A command-line tool for managing your Advent of Code environment.
    This tool helps you fetch puzzle data, submit answers, and manage solutions.
    """
    pass

@cli.command()
def setup():
    """
    Runs an interactive wizard to configure your environment.
    This will ask for your Advent of Code session cookie.
    """
    click.echo("--- Advent of Code Environment Setup ---")
    click.echo("\nThis wizard will help you configure your session cookie.")
    click.echo("You can get your cookie from the Advent of Code website:")
    click.echo("  1. Log in to https://adventofcode.com")
    click.echo("  2. Open your browser's developer tools (usually by pressing F12).")
    click.echo("  3. Go to the 'Application' or 'Storage' tab.")
    click.echo("  4. Find the 'Cookies' section for adventofcode.com.")
    click.echo("  5. Copy the entire value of the 'session' cookie.")

    # Prompt for the cookie securely (hides input)
    session_cookie = click.prompt("\nPlease paste your session cookie", hide_input=True)

    # Save the cookie to the config file
    config = configparser.ConfigParser()
    config["user"] = {"session_cookie": session_cookie}

    try:
        with open(CONFIG_FILE_PATH, "w") as config_file:
            config.write(config_file)
        click.secho(f"\n✅ Configuration saved successfully to {CONFIG_FILE_PATH}", fg="green")
    except Exception as e:
        click.secho(f"\n❌ Error saving configuration: {e}", fg="red")

if __name__ == "__main__":
    cli()
