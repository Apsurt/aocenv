import click
import configparser
from pathlib import Path
import logging
import colorlog
import aoc
import os
import subprocess
import time
import shutil
import datetime
import json
import shutil
from .stats_viewer import StatsApp

# --- PATHS & CONFIG ---
PROJECT_ROOT = Path(__file__).parent.parent.parent
CONFIG_FILE_PATH = PROJECT_ROOT / "env_src" / "config.ini"
LOGS_DIR = PROJECT_ROOT / ".logs"
CACHE_DIR = PROJECT_ROOT / ".cache"
SOLUTIONS_DIR = PROJECT_ROOT / "solutions"
NOTEPAD_PATH = PROJECT_ROOT / "notepad.py"
PROGRESS_JSON_PATH = PROJECT_ROOT / "progress.json"

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
    required_dirs = [CACHE_DIR, LOGS_DIR, SOLUTIONS_DIR]
    for directory in required_dirs:
        directory.mkdir(exist_ok=True)
        # Also ensure .gitkeep exists so the folder structure can be committed
        gitkeep_path = directory / ".gitkeep"
        if not gitkeep_path.exists():
            gitkeep_path.touch()
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

@cli.command(hidden=True)
def nuke():
    """
    Deletes all cached data, logs, solutions, and config.

    This is a destructive operation and cannot be undone.
    """
    logger = logging.getLogger(__name__)

    dirs_to_clear = [CACHE_DIR, LOGS_DIR, SOLUTIONS_DIR]

    click.secho("🔥 NUKE WARNING 🔥", fg="red", bold=True, blink=True)
    click.echo("This command will permanently delete the CONTENTS of:")
    click.echo(f"  - Notepad: {NOTEPAD_PATH}")
    click.echo(f"  - Cache: {CACHE_DIR}")
    click.echo(f"  - Solutions: {SOLUTIONS_DIR}")
    click.echo(f"  - Logs: {LOGS_DIR}")
    click.echo(f"  - And your configuration file: {CONFIG_FILE_PATH}")

    click.confirm("\nAre you absolutely sure you want to proceed?", abort=True)

    logger.info("Proceeding with nuke operation...")

    try:
        for directory in dirs_to_clear:
            if not directory.exists():
                continue
            logger.info(f"Clearing contents of {directory}...")
            for item in directory.iterdir():
                # IMPORTANT: Do not delete the .gitkeep file
                if item.name == ".gitkeep":
                    continue
                if item.is_dir():
                    shutil.rmtree(item)
                else:
                    item.unlink()

        if NOTEPAD_PATH.exists():
            NOTEPAD_PATH.unlink()
            NOTEPAD_PATH.write_text("")
            logger.info("Cleared notepad.py file.")

        # Delete the config file
        if CONFIG_FILE_PATH.exists():
            CONFIG_FILE_PATH.unlink()
            logger.info("Deleted configuration file.")

        click.secho("\n✅ Environment has been wiped clean.", fg="green")
        click.echo("Run 'aoc setup' to re-configure.")

    except Exception as e:
        logger.error(f"An error occurred during the nuke operation: {e}")

@cli.command()
@click.argument('part', type=click.Choice(['1', '2']))
@click.option("-y", "--year", default=None, type=int, help="The puzzle year. Defaults to latest.")
@click.option("-d", "--day", default=None, type=int, help="The puzzle day. Defaults to latest.")
@click.option("-f", "--force", is_flag=True, help="Force overwrite of notepad.py if not empty.")
def load(part, year, day, force):
    """
    Loads a saved solution into notepad.py.

    PART is the puzzle part to load (1 or 2).
    """
    logger = logging.getLogger(__name__)

    # 1. Determine the target year and day
    target_year = year if year is not None else aoc.year
    target_day = day if day is not None else aoc.day
    target_part = int(part)

    # 2. Check if the solution file exists
    solution_path = SOLUTIONS_DIR / str(target_year) / f"{target_day:02d}" / f"part_{target_part}.py"
    logger.info(f"Attempting to load solution from: {solution_path}")

    if not solution_path.exists():
        click.secho(f"Error: Solution not found at {solution_path}", fg="red")
        return

    # 3. Check if notepad.py is empty and handle confirmation/force
    if NOTEPAD_PATH.exists() and NOTEPAD_PATH.read_text().strip() and not force:
        click.secho("Warning: notepad.py is not empty!", fg="yellow")
        if not click.confirm("Do you want to overwrite its contents?"):
            click.echo("Load operation cancelled.")
            return

    # 4. Perform the file copy
    try:
        solution_content = solution_path.read_text()
        NOTEPAD_PATH.write_text(solution_content)
        click.secho(f"✅ Successfully loaded Part {part} for {target_year}-{target_day:02d} into notepad.py.", fg="green")
    except Exception as e:
        logger.error(f"Failed to load solution into notepad.py: {e}")

@cli.command()
@click.option("-f", "--force", is_flag=True, help="Force sync even if it was run recently.")
def sync(force):
    """
    Scrapes AoC website for your progress and caches all puzzle texts and answers.

    This is a long-running command that makes many requests. Use it sparingly.
    By default, this command can only be run once every 24 hours.
    """
    logger = logging.getLogger(__name__)

    if not force and PROGRESS_JSON_PATH.exists():
        with open(PROGRESS_JSON_PATH, 'r') as f:
            try:
                data = json.load(f)
                last_sync_str = data.get("last_sync_timestamp")
                if last_sync_str:
                    last_sync_time = datetime.datetime.fromisoformat(last_sync_str)
                    if datetime.datetime.now(datetime.timezone.utc) - last_sync_time < datetime.timedelta(days=1):
                        display_time = last_sync_time.astimezone()
                        click.secho(f"Sync was already performed at {display_time.strftime('%Y-%m-%d %H:%M:%S')}.", fg="yellow")
                        click.echo("Please wait 24 hours or use the --force flag to override.")
                        return
            except json.JSONDecodeError:
                logger.warning("Could not parse progress.json, proceeding with sync.")

    click.secho("Starting full sync with Advent of Code website...", fg="yellow")

    # PASS 1: Discover all tasks that need to be run.
    logger.info("Discovering puzzles to sync...")
    now = datetime.datetime.now(datetime.timezone.utc) # Use timezone-aware
    latest_year_to_check = now.year if now.month == 12 else now.year - 1
    tasks_to_run = []
    full_progress = {}

    for year in range(2015, latest_year_to_check + 1):
        try:
            year_progress = aoc._utils.scrape_year_progress(year)
            if not year_progress:
                continue
            full_progress[str(year)] = year_progress
            for day_str, star_count in year_progress.items():
                tasks_to_run.append({"year": year, "day": int(day_str), "stars": star_count})
        except Exception as e:
            logger.error(f"Failed to discover progress for year {year}: {e}")

    click.echo(f"Found {len(tasks_to_run)} puzzles to sync. Starting download...")

    # PASS 2: Execute the tasks with a progress bar.
    def run_task(task):
        """Helper function to process a single task. No logging here."""
        year, day, stars = task['year'], task['day'], task['stars']
        aoc._utils.get_aoc_data(year, day, "instructions")
        if stars > 0:
            correct_answers = aoc._utils.scrape_day_page_for_answers(year, day)
            if correct_answers:
                answers_cache = aoc._utils._read_answers_cache(year, day)
                for part, answer in correct_answers.items():
                    part_key = f"part_{part}"
                    answers_cache[part_key]["correct_answer"] = answer
                aoc._utils._write_answers_cache(year, day, answers_cache)
        # time.sleep(0.25)

    def show_current_task(task):
        """Provides the text to display next to the progress bar."""
        if task:
            return f"Syncing {task['year']}-{task['day']:02d}"
        return "" # Message when bar is finished

    with click.progressbar(
        tasks_to_run,
        label="Syncing puzzle data",
        length=len(tasks_to_run),
        item_show_func=show_current_task
    ) as bar:
        for task in bar:
            run_task(task)

    # Save the aggregated progress data
    data_to_save = {
        "last_sync_timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "progress": full_progress
    }
    with open(PROGRESS_JSON_PATH, 'w') as f:
        json.dump(data_to_save, f, indent=2, sort_keys=True)

    click.secho("\n✅ Sync complete!", fg="green")
    click.echo(f"Your progress has been saved to {PROGRESS_JSON_PATH}")
    click.echo("You can now use the 'aoc stats'")

@cli.command()
def stats():
    """
    Launches an interactive viewer for your puzzle completion stats.
    """
    logger = logging.getLogger(__name__)
    if not PROGRESS_JSON_PATH.exists():
        click.secho("No progress data found.", fg="red")
        click.echo("Please run 'aoc sync' first to gather your data.")
        return

    with open(PROGRESS_JSON_PATH, 'r') as f:
        progress_data = json.load(f).get("progress", {})

    if not progress_data:
        click.secho("Progress data is empty. Run 'aoc sync' to gather data.", fg="yellow")
        return

    # Launch the Textual app, passing the progress data to it
    app = StatsApp(progress_data=progress_data)
    app.run()

@cli.command()
@click.option("-f", "--force", is_flag=True, help="Force overwrite of notepad.py if not empty.")
def start(force):
    """
    Populates notepad.py with a boilerplate template for a new puzzle.
    """
    logger = logging.getLogger(__name__)

    # 1. Safety Check: aoc load
    if NOTEPAD_PATH.exists() and NOTEPAD_PATH.read_text().strip() and not force:
        click.secho("Warning: notepad.py is not empty!", fg="yellow")
        if not click.confirm("Do you want to overwrite its contents with the template?"):
            click.echo("Operation cancelled.")
            return

    # 2. Get latest puzzle date to suggest in the template
    latest_year, latest_day = aoc._utils.get_latest_puzzle_date()

    # 3. Define the boilerplate template
    boilerplate =f"""import aoc

# --- Context Setting ---
# By default, the environment will use the latest puzzle.
# You can override it by uncommenting and setting the year/day below.

# aoc.year = {latest_year}
# aoc.day = {latest_day}
aoc.part = 1

# --- Puzzle Logic ---
# Get the puzzle input. The 'get_input' function will be automatically
# populated with the aoc.year and aoc.day context.

# puzzle_input = aoc.get_input()

# Your solution logic here...
def your_function_name():
    return

answer = your_function_name()

# --- Submission ---
# After solving, uncomment the following lines to submit your answer.

# if answer is not None:
#     print(aoc.submit(answer))

# --- Binding ---
# If you don't have automated binding enabled uncomment this line:

# aoc.bind()
"""

    # 4. Write the template to the file
    try:
        # We use strip() to remove the leading indentation from the multiline string
        NOTEPAD_PATH.write_text(boilerplate.strip())
        click.secho(f"✅ notepad.py has been populated with the boilerplate for {latest_year}-{latest_day:02d}.", fg="green")
    except Exception as e:
        logger.error(f"Failed to write boilerplate to notepad.py: {e}")

if __name__ == "__main__":
    cli()
