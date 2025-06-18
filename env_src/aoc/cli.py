import click
import configparser
from pathlib import Path
import logging
import colorlog
import aoc
import subprocess
import time
import shutil
import datetime
import json
import re
import os
from .stats_viewer import StatsApp
from aoc import _utils

# --- PATHS & CONFIG ---
PROJECT_ROOT = Path(__file__).parent.parent.parent
CONFIG_FILE_PATH = PROJECT_ROOT / "env_src" / "config.ini"
LOGS_DIR = PROJECT_ROOT / ".logs"
CACHE_DIR = PROJECT_ROOT / ".cache"
SOLUTIONS_DIR = PROJECT_ROOT / "solutions"
NOTEPAD_PATH = PROJECT_ROOT / "notepad.py"
TEMPLATES_DIR = PROJECT_ROOT / ".templates"
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

@cli.group()
def context():
    """Manages the persistent puzzle context (year and day)."""
    pass

@context.command(name="set")
@click.option("-y", "--year", type=int, required=True, help="The puzzle year to set.")
@click.option("-d", "--day", type=int, required=True, help="The puzzle day to set.")
def context_set(year, day):
    """Sets and saves the puzzle context."""
    _utils.write_context(year, day)
    click.secho(f"✅ Context set to Year {year}, Day {day}.", fg="green")

@context.command(name="show")
def context_show():
    """Displays the current puzzle context."""
    context = _utils.read_context()
    if context:
        year, day = context
        click.echo(f"The current context is set to: Year {year}, Day {day}")
    else:
        click.echo("No context is currently set.")
        click.echo("The tool will default to the latest available puzzle.")

@context.command(name="clear")
def context_clear():
    """Clears the saved puzzle context."""
    _utils.clear_context()
    click.secho("✅ Context cleared.", fg="green")
    click.echo("The tool will now default to the latest available puzzle.")


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

    session_cookie = click.prompt("\nPlease paste your session cookie", hide_input=True)
    auto_bind = click.confirm("\nAutomatically save your code (`bind`) on a correct submission?", default=True)
    auto_clear = click.confirm("\nAutomatically clear notepad.py after a successful bind?", default=False)
    auto_commit = click.confirm("\nAutomatically commit solutions to Git after a successful bind?", default=True)

    config = configparser.ConfigParser()
    config["user"] = {
        "session_cookie": session_cookie,
        "auto_bind": "true" if auto_bind else "false",
        "auto_clear_on_bind": "true" if auto_clear else "false",
        "auto_commit_on_bind": "true" if auto_commit else "false"
    }

    try:
        with open(CONFIG_FILE_PATH, "w") as config_file:
            config.write(config_file)
        click.secho(f"\n✅ Configuration saved successfully to {CONFIG_FILE_PATH}", fg="green")
    except Exception as e:
        click.secho(f"\n❌ Error saving configuration: {e}", fg="red")

@cli.command()
def text():
    """Displays the puzzle instructions for the current context."""
    click.echo(f"--- 🗓️ Advent of Code {aoc.year} - Day {aoc.day} --- \n")
    try:
        instruction_text = aoc.get_instructions()
        click.echo(instruction_text)
    except Exception as e:
        click.secho(f"❌ Error fetching instructions: {e}", fg="red")

@cli.command()
def input():
    """Fetches and displays the puzzle input for the current context."""
    logger = logging.getLogger(__name__)
    logger.info(f"Getting input for {aoc.year}-{aoc.day}")
    try:
        input_text = aoc.get_input()
        click.echo(f"--- Puzzle Input for {aoc.year}-{aoc.day} ---")
        click.echo(input_text)
    except Exception as e:
        logger.error(f"Failed to get input: {e}")

@cli.command()
@click.option('-t', '--time', 'time_it', is_flag=True, help="Time the execution of the script.")
def run(time_it):
    """Executes the code in the main notepad.py file."""
    logger = logging.getLogger(__name__)

    if not NOTEPAD_PATH.exists():
        logger.error(f"Notepad file not found at: {NOTEPAD_PATH}")
        return

    start_time = 0
    if time_it:
        start_time = time.perf_counter()

    logger.info(f"Executing {NOTEPAD_PATH} with context {aoc.year}-{aoc.day}...")
    try:
        subprocess.run(["python", NOTEPAD_PATH], check=True)
    except subprocess.CalledProcessError as e:
        logger.error(f"notepad.py exited with an error (return code {e.returncode}).")
    except Exception as e:
        logger.error(f"An unexpected error occurred while running notepad.py: {e}")
    finally:
        if time_it:
            end_time = time.perf_counter()
            duration_ms = (end_time - start_time) * 1000
            click.secho(f"\n⏱️ Execution time: {duration_ms:.2f} ms", fg="yellow")

@cli.command()
@click.argument('part', type=click.Choice(['1', '2']))
@click.option("-f", "--force", is_flag=True, help="Force overwrite of notepad.py if not empty.")
def load(part, force):
    """
    Loads a saved solution for the current context into notepad.py.
    PART is the puzzle part to load (1 or 2).
    """
    logger = logging.getLogger(__name__)
    target_year, target_day, target_part = aoc.year, aoc.day, int(part)

    solution_path = SOLUTIONS_DIR / str(target_year) / f"{target_day:02d}" / f"part_{target_part}.py"
    logger.info(f"Attempting to load solution from: {solution_path}")

    if not solution_path.exists():
        click.secho(f"Error: Solution not found at {solution_path}", fg="red")
        return

    if NOTEPAD_PATH.exists() and NOTEPAD_PATH.read_text().strip() and not force:
        click.secho("Warning: notepad.py is not empty!", fg="yellow")
        if not click.confirm("Do you want to overwrite its contents?"):
            click.echo("Load operation cancelled.")
            return

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
    now = datetime.datetime.now(datetime.timezone.utc)
    latest_year_to_check = now.year if now.month == 12 else now.year - 1
    tasks_to_run = []
    full_progress = {}

    for year in range(2015, latest_year_to_check + 1):
        try:
            year_progress = _utils.scrape_year_progress(year)
            if not year_progress:
                continue
            full_progress[str(year)] = year_progress
            for day_str, star_count in year_progress.items():
                tasks_to_run.append({"year": year, "day": int(day_str), "stars": star_count})
        except Exception as e:
            logger.error(f"Failed to discover progress for year {year}: {e}")

    click.echo(f"Found {len(tasks_to_run)} puzzles to sync. Starting download...")

    def run_task(task):
        year, day, stars = task['year'], task['day'], task['stars']
        _utils.get_aoc_data(year, day, "instructions")
        if stars > 0:
            correct_answers = _utils.scrape_day_page_for_answers(year, day)
            if correct_answers:
                answers_cache = _utils._read_answers_cache(year, day)
                for part, answer in correct_answers.items():
                    part_key = f"part_{part}"
                    answers_cache[part_key]["correct_answer"] = answer
                _utils._write_answers_cache(year, day, answers_cache)

    with click.progressbar(tasks_to_run, label="Syncing puzzle data", length=len(tasks_to_run)) as bar:
        for task in bar:
            run_task(task)

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
    """Launches an interactive viewer for your puzzle completion stats."""
    logger = logging.getLogger(__name__)
    if not PROGRESS_JSON_PATH.exists():
        click.secho("No progress data found. Please run 'aoc sync' first.", fg="red")
        return
    with open(PROGRESS_JSON_PATH, 'r') as f:
        progress_data = json.load(f).get("progress", {})
    if not progress_data:
        click.secho("Progress data is empty. Run 'aoc sync' to gather data.", fg="yellow")
        return
    app = StatsApp(progress_data=progress_data)
    app.run()


@cli.command()
@click.argument('name', default='default', required=False)
@click.option("-f", "--force", is_flag=True, help="Force overwrite of notepad.py if not empty.")
def start(name, force):
    """Populates notepad.py with a template."""
    ctx = click.get_current_context()
    ctx.invoke(template_load, name=name, force=force)


@cli.command()
def clear():
    """Clears all content from the notepad.py file."""
    aoc.clear()
    click.secho("✅ notepad.py has been cleared.", fg="green")


@cli.command(name="list")
def solutions_list():
    """Lists all archived solutions."""
    if not SOLUTIONS_DIR.exists():
        click.echo("No solutions directory found.")
        return
    solution_files = sorted(SOLUTIONS_DIR.glob("**/part_*.py"), reverse=True)
    if not solution_files:
        click.echo("No solutions have been saved yet.")
        return
    click.secho("--- Archived Solutions ---", bold=True)
    last_year = None
    for path in solution_files:
        try:
            year, day, part = path.parts[-3], path.parts[-2], path.stem
            if year != last_year:
                click.secho(f"\nYear {year}", fg="bright_yellow")
                last_year = year
            click.echo(f"  Day {day}, {part.replace('_', ' ').title()}")
        except IndexError:
            continue

@cli.group()
def template():
    """Manages custom user templates."""
    pass

@template.command(name="save")
@click.argument('name')
@click.option("-f", "--force", is_flag=True, help="Force overwrite of an existing template.")
def template_save(name, force):
    """Saves the current content of notepad.py as a new template."""
    logger = logging.getLogger(__name__)
    template_path = TEMPLATES_DIR / f"{name}.py.template"

    if template_path.exists() and not force:
        click.secho(f"Error: Template '{name}' already exists. Use --force to overwrite.", fg="red")
        return

    try:
        content = NOTEPAD_PATH.read_text()
        template_path.write_text(content)
        click.secho(f"✅ Template '{name}' saved successfully.", fg="green")
    except Exception as e:
        logger.error(f"Failed to save template: {e}")

@template.command(name="load")
@click.argument('name')
@click.option("-f", "--force", is_flag=True, help="Force overwrite of notepad.py if not empty.")
def template_load(name, force):
    """Loads a template into notepad.py."""
    logger = logging.getLogger(__name__)
    template_path = TEMPLATES_DIR / f"{name}.py.template"

    if not template_path.exists():
        click.secho(f"Error: Template '{name}' not found.", fg="red")
        return

    if NOTEPAD_PATH.exists() and NOTEPAD_PATH.read_text().strip() and not force:
        click.secho("Warning: notepad.py is not empty!", fg="yellow")
        if not click.confirm("Do you want to overwrite its contents?"):
            click.echo("Load operation cancelled.")
            return

    try:
        content = template_path.read_text()
        NOTEPAD_PATH.write_text(content)
        click.secho(f"✅ Template '{name}' loaded into notepad.py.", fg="green")
    except Exception as e:
        logger.error(f"Failed to load template: {e}")

@template.command(name="list")
def template_list():
    """Lists all available custom templates."""
    if not TEMPLATES_DIR.exists() or not any(TEMPLATES_DIR.iterdir()):
        click.echo("No custom templates found.")
        return

    click.secho("--- Custom Templates ---", bold=True)
    for template_file in sorted(TEMPLATES_DIR.glob("*.py.template")):
        click.echo(f"  - {template_file.stem.replace('.py', '')}")

@template.command(name="delete")
@click.argument('name')
def template_delete(name):
    """Deletes a saved template."""
    if name.lower() == 'default':
        click.secho("Error: The 'default' template is protected.", fg="red")
        return

    template_path = TEMPLATES_DIR / f"{name}.py.template"

    if not template_path.exists():
        click.secho(f"Error: Template '{name}' not found.", fg="red")
        return

    if click.confirm(f"Are you sure you want to delete the template '{name}'?"):
        try:
            template_path.unlink()
            click.secho(f"✅ Template '{name}' deleted.", fg="green")
        except Exception as e:
            logging.getLogger(__name__).error(f"Failed to delete template: {e}")
    else:
        click.echo("Delete operation cancelled.")

@cli.group()
def test():
    """Manages and runs test cases for puzzles."""
    pass

@test.command(name="add")
@click.option("-p", "--part", type=click.Choice(['1', '2']), prompt="Which part is this test for? (1 or 2)")
def test_add(part):
    """Interactively add a new test case for the current context."""
    target_year, target_day = aoc.year, aoc.day
    part_key = f"part_{part}"

    click.echo(f"--- Adding New Test Case for {target_year}-{target_day} Part {part} ---")
    test_input = click.edit()
    if test_input is None:
        click.echo("No input provided. Aborting.")
        return
    test_output = click.prompt("What is the expected output?")

    tests_data = _utils._read_tests_cache(target_year, target_day)
    tests_data[part_key].append({"input": test_input.strip(), "output": test_output.strip()})
    _utils._write_tests_cache(target_year, target_day, tests_data)
    click.secho("\n✅ Test case added successfully!", fg="green")


@test.command(name="list")
def test_list():
    """Lists saved test cases for the current context."""
    target_year, target_day = aoc.year, aoc.day
    tests_data = _utils._read_tests_cache(target_year, target_day)

    click.secho(f"--- Test Cases for {target_year}-{target_day:02d} ---", bold=True)
    total_tests = len(tests_data["part_1"]) + len(tests_data["part_2"])
    if total_tests == 0:
        click.echo("No test cases found. Add one with 'aoc test add'.")
        return

    for part_num in [1, 2]:
        part_key = f"part_{part_num}"
        if tests_data[part_key]:
            click.secho(f"\nPart {part_num}:", fg="yellow")
            for i, test in enumerate(tests_data[part_key]):
                click.secho(f"  Test #{i+1}:", bold=True)
                indented_input = "    " + "\n    ".join(test['input'].splitlines())
                click.secho(f"    --- Input ---\n{indented_input}", fg="bright_black")
                click.echo(f"    --- Expected Output ---\n    {test['output']}")


@test.command(name="delete")
@click.argument('part', type=click.Choice(['1', '2']))
@click.argument('index', type=int)
def test_delete(part, index):
    """Deletes a specific test case for the current context."""
    target_year, target_day = aoc.year, aoc.day
    part_key = f"part_{part}"
    list_index = index - 1

    tests_data = _utils._read_tests_cache(target_year, target_day)

    if not (0 <= list_index < len(tests_data[part_key])):
        click.secho(f"Error: Test #{index} for Part {part} does not exist.", fg="red")
        return

    tests_data[part_key].pop(list_index)
    _utils._write_tests_cache(target_year, target_day, tests_data)
    click.secho(f"✅ Test #{index} for Part {part} has been deleted.", fg="green")


@test.command(name="run")
def test_run():
    """Runs notepad.py against all saved tests for the current context."""
    logger = logging.getLogger(__name__)
    target_year, target_day = aoc.year, aoc.day

    try:
        notepad_content = NOTEPAD_PATH.read_text()
        part_match = re.search(r"aoc\.submit\s*\(\s*[^,]+,\s*part\s*=\s*([12])\s*\)", notepad_content)
        if not part_match:
             part_match = re.search(r"aoc\.bind\s*\(\s*part\s*=\s*([12])\s*\)", notepad_content)

        if not part_match:
            click.secho("Error: Could not determine part from notepad.py.", fg="red")
            click.secho("Hint: Make sure you have an `aoc.submit(answer, part=1)` or `aoc.bind(part=1)` call.", fg="red")
            return
        part = int(part_match.group(1))
        part_key = f"part_{part}"
    except FileNotFoundError:
        click.secho(f"Error: notepad.py not found.", fg="red")
        return

    tests_data = _utils._read_tests_cache(target_year, target_day)
    tests_to_run = tests_data.get(part_key, [])
    if not tests_to_run:
        click.echo(f"No test cases found for Part {part}. Add one with 'aoc test add'.")
        return

    click.secho(f"--- Running {len(tests_to_run)} Test(s) for Part {part} ---", bold=True)
    passed_count = 0

    for i, test in enumerate(tests_to_run):
        click.secho(f"\n--- Test Case #{i+1} ---", fg="yellow")
        test_env = os.environ.copy()
        test_env["AOC_TEST_MODE"] = "true"
        test_env["AOC_TEST_INPUT"] = test["input"]
        test_env["AOC_TEST_OUTPUT"] = test["output"]

        try:
            result = subprocess.run(
                ["python", NOTEPAD_PATH],
                capture_output=True, text=True, env=test_env
            )
            output = result.stdout.strip()
            click.echo(output)
            if result.stderr:
                click.secho(result.stderr.strip(), fg='red')
            if "✅ PASSED" in output:
                passed_count += 1
        except Exception as e:
            logger.error(f"An unexpected error occurred running test #{i+1}: {e}")

    color = "green" if passed_count == len(tests_to_run) else "red"
    click.secho(f"\n--- Summary ---\n{passed_count} / {len(tests_to_run)} tests passed.", fg=color, bold=True)

if __name__ == "__main__":
    cli()
