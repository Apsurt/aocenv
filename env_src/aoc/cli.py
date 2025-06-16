import click
import configparser
from pathlib import Path
import logging
import colorlog
import aoc
import os
import subprocess
import time

# --- PATHS & CONFIG ---
PROJECT_ROOT = Path(__file__).parent.parent.parent
CONFIG_FILE_PATH = Path(__file__).parent.parent / "config.ini"
LOGS_DIR = Path(__file__).parent.parent.parent / ".logs"
NOTEPAD_PATH = PROJECT_ROOT / "notepad.py"

def setup_logging(verbose: bool):
    """Configures file and console logging."""
    # Ensure the logs directory exists
    LOGS_DIR.mkdir(exist_ok=True)

    # Get the root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO) # Set the lowest level for the root logger

    # --- File Handler (always logs at INFO level) ---
    file_handler = logging.FileHandler(LOGS_DIR / "aoc_env.log")
    file_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    file_handler.setFormatter(file_formatter)
    root_logger.addHandler(file_handler)

    # --- Console Handler (level depends on verbose flag) ---
    console_handler = colorlog.StreamHandler()

    # Set console log level based on the verbose flag
    if verbose:
        console_handler.setLevel(logging.INFO)
    else:
        console_handler.setLevel(logging.WARNING) # Hide INFO unless -v is used

    # Create a color formatter
    console_formatter = colorlog.ColoredFormatter(
        '%(log_color)s%(levelname)s: %(message)s',
        log_colors={
            'DEBUG':    'cyan',
            'INFO':     'green',
            'WARNING':  'yellow',
            'ERROR':    'red',
            'CRITICAL': 'red,bg_white',
        }
    )
    console_handler.setFormatter(console_formatter)
    root_logger.addHandler(console_handler)

# The context_settings allows the -v flag to work on the main command
@click.group(context_settings=dict(help_option_names=['-h', '--help']))
@click.option('-v', '--verbose', is_flag=True, help="Enable verbose informational logging.")
def cli(verbose):
    """
    A command-line tool for managing your Advent of Code environment.
    This tool helps you fetch puzzle data, submit answers, and manage solutions.
    """
    setup_logging(verbose)

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

    auto_bind = click.confirm(
            "\nAutomatically save your code (`bind`) on a correct submission?",
            default=True
        )

    # Save the cookie to the config file
    config = configparser.ConfigParser()
    config["user"] = {
            "session_cookie": session_cookie,
            "auto_bind": "true" if auto_bind else "false"
        }

    try:
        with open(CONFIG_FILE_PATH, "w") as config_file:
            config.write(config_file)
        click.secho(f"\n✅ Configuration saved successfully to {CONFIG_FILE_PATH}", fg="green")
    except Exception as e:
        click.secho(f"\n❌ Error saving configuration: {e}", fg="red")

@cli.command()
@click.option("--year", "-y", default=None, type=int, help="The puzzle year. Defaults to latest.")
@click.option("--day", "-d", default=None, type=int, help="The puzzle day. Defaults to latest.")
def text(year, day):
    """
    Fetches and displays the puzzle instructions for a given day.
    """
    # Override the default context if flags are provided
    if year:
        aoc.year = year
    if day:
        aoc.day = day

    click.echo(f"--- 🗓️ Advent of Code {aoc.year} - Day {aoc.day} --- \n")
    try:
        instruction_text = aoc.get_instructions()
        click.echo(instruction_text)
    except Exception as e:
        click.secho(f"❌ Error fetching instructions: {e}", fg="red")

@cli.command()
@click.option("-y", "--year", default=None, type=int, help="The puzzle year. Defaults to latest.")
@click.option("-d", "--day", default=None, type=int, help="The puzzle day. Defaults to latest.")
def input(year, day):
    """
    Fetches and displays the puzzle input for a given day.
    """
    # Override the default context if flags are provided
    if year:
        aoc.year = year
    if day:
        aoc.day = day

    logger = logging.getLogger(__name__)
    logger.info(f"Getting input for {aoc.year}-{aoc.day}")
    try:
        input_text = aoc.get_input()
        click.echo("--- Puzzle Input ---")
        click.echo(input_text)
    except Exception as e:
        logger.error(f"Failed to get input: {e}")

@cli.command()
@click.option('-t', '--time', 'time_it', is_flag=True, help="Time the execution of the script.")
def run(time_it):
    """
    Executes the code in the main notepad.py file.
    """
    logger = logging.getLogger(__name__)

    if not NOTEPAD_PATH.exists():
        logger.error(f"Notepad file not found at: {NOTEPAD_PATH}")
        return

    # --- Timing Logic ---
    start_time = 0
    if time_it:
        # time.perf_counter() is best for measuring short durations
        start_time = time.perf_counter()

    logger.info(f"Executing {NOTEPAD_PATH}...")
    try:
        # Use subprocess to run the script
        subprocess.run(["python", NOTEPAD_PATH], check=True)
    except subprocess.CalledProcessError as e:
        logger.error(f"notepad.py exited with an error (return code {e.returncode}).")
    except Exception as e:
        logger.error(f"An unexpected error occurred while running notepad.py: {e}")
    finally:
        # --- Timing Logic ---
        if time_it:
            end_time = time.perf_counter()
            duration_ms = (end_time - start_time) * 1000
            # Use secho for colored output
            click.secho(f"\n⏱️ Execution time: {duration_ms:.2f} ms", fg="yellow")

if __name__ == "__main__":
    cli()
