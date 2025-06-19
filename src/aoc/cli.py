import collections
import configparser
import datetime
import json
import logging
import os
import re
import statistics
import subprocess

import click
import colorlog
from tabulate import tabulate

import aoc
from aoc import _utils

# --- Command Imports ---
from .cli_commands.context import context_group
from .cli_commands.template import template_group
from .cli_commands.test import test_group


def setup_logging(verbose: bool):
	"""Configures file and console logging."""
	_utils.LOGS_DIR.mkdir(exist_ok=True)
	root_logger = logging.getLogger()
	root_logger.setLevel(logging.INFO)

	file_handler = logging.FileHandler(_utils.LOGS_DIR / "aoc_env.log")
	file_formatter = logging.Formatter(
		"%(asctime)s - %(name)s - %(levelname)s - %(message)s"
	)
	file_handler.setFormatter(file_formatter)
	root_logger.addHandler(file_handler)

	console_handler = colorlog.StreamHandler()
	if verbose:
		console_handler.setLevel(logging.INFO)
	else:
		console_handler.setLevel(logging.WARNING)

	console_formatter = colorlog.ColoredFormatter(
		"%(log_color)s%(levelname)s: %(message)s",
		log_colors={
			"DEBUG": "cyan",
			"INFO": "green",
			"WARNING": "yellow",
			"ERROR": "red",
			"CRITICAL": "red,bg_white",
		},
	)
	console_handler.setFormatter(console_formatter)
	root_logger.addHandler(console_handler)


@click.group(context_settings=dict(help_option_names=["-h", "--help"]))
@click.option(
	"-v", "--verbose", is_flag=True, help="Enable verbose informational logging."
)
def cli(verbose):
	"""
	A command-line tool for managing your Advent of Code environment.
	This tool helps you fetch puzzle data, submit answers, and manage solutions.
	"""
	required_dirs = [_utils.CACHE_DIR, _utils.LOGS_DIR, _utils.SOLUTIONS_DIR]
	for directory in required_dirs:
		directory.mkdir(exist_ok=True)
		gitkeep_path = directory / ".gitkeep"
		if not gitkeep_path.exists():
			gitkeep_path.touch()
	setup_logging(verbose)


# --- Standalone Commands ---


@cli.command()
def setup():
	"""Runs an interactive wizard to configure your environment."""
	click.echo("--- Advent of Code Environment Setup ---")
	click.echo("\nThis wizard will help you configure your session cookie.")
	click.echo("You can get your cookie from the Advent of Code website:")
	click.echo("  1. Log in to https://adventofcode.com")
	click.echo("  2. Open your browser's developer tools (usually by pressing F12).")
	click.echo("  3. Go to the 'Application' or 'Storage' tab.")
	click.echo("  4. Find the 'Cookies' section for adventofcode.com.")
	click.echo("  5. Copy the entire value of the 'session' cookie.")

	session_cookie = click.prompt("\nPlease paste your session cookie", hide_input=True)
	auto_bind = click.confirm(
		"\nAutomatically save your code (`bind`) on a correct submission?", default=True
	)
	auto_clear = click.confirm(
		"\nAutomatically clear notepad.py after a successful bind?", default=False
	)
	auto_commit = click.confirm(
		"\nAutomatically commit solutions to Git after a successful bind?", default=True
	)
	auto_format = click.confirm(
		"\nAutomatically format notepad.py with ruff on bind?", default=True
	)

	config = configparser.ConfigParser()
	config["user"] = {
		"session_cookie": session_cookie,
		"auto_bind": "true" if auto_bind else "false",
		"auto_clear_on_bind": "true" if auto_clear else "false",
		"auto_commit_on_bind": "true" if auto_commit else "false",
		"auto_format_on_bind": "true" if auto_format else "false",
	}
	try:
		with open(_utils.CONFIG_FILE_PATH, "w") as config_file:
			config.write(config_file)
		click.secho(
			f"\n✅ Configuration saved successfully to {_utils.CONFIG_FILE_PATH}",
			fg="green",
		)
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
@click.option(
	"-t",
	"--time",
	"time_it",
	is_flag=True,
	help="Time the execution of the script's core logic.",
)
def run(time_it):
	"""Executes the code in the main notepad.py file."""
	logger = logging.getLogger(__name__)
	if not _utils.NOTEPAD_PATH.exists():
		logger.error(f"Notepad file not found at: {_utils.NOTEPAD_PATH}")
		return
	env = os.environ.copy()
	if time_it:
		env["AOC_TIME_IT"] = "true"
	logger.info(f"Executing {_utils.NOTEPAD_PATH} with context {aoc.year}-{aoc.day}...")
	try:
		subprocess.run(["python", str(_utils.NOTEPAD_PATH)], check=True, env=env)
	except subprocess.CalledProcessError as e:
		logger.error(f"notepad.py exited with an error (return code {e.returncode}).")
	except Exception as e:
		logger.error(f"An unexpected error occurred while running notepad.py: {e}")


@cli.command()
@click.argument("part", type=click.Choice(["1", "2"]))
@click.option(
	"-f", "--force", is_flag=True, help="Force overwrite of notepad.py if not empty."
)
def load(part, force):
	"""Loads a saved solution for the current context into notepad.py."""
	logger = logging.getLogger(__name__)
	target_year, target_day, target_part = aoc.year, aoc.day, int(part)
	solution_path = (
		_utils.SOLUTIONS_DIR
		/ str(target_year)
		/ f"{target_day:02d}"
		/ f"part_{target_part}.py"
	)
	logger.info(f"Attempting to load solution from: {solution_path}")
	if not solution_path.exists():
		click.secho(f"Error: Solution not found at {solution_path}", fg="red")
		return
	if (
		_utils.NOTEPAD_PATH.exists()
		and _utils.NOTEPAD_PATH.read_text().strip()
		and not force
	):
		if not click.confirm("Warning: notepad.py is not empty! Overwrite it?"):
			click.echo("Load operation cancelled.")
			return
	try:
		solution_content = solution_path.read_text()
		_utils.NOTEPAD_PATH.write_text(solution_content)
		click.secho(
			f"✅ Successfully loaded Part {part} for {target_year}-"
			f"{target_day:02d} into notepad.py.",
			fg="green",
		)
	except Exception as e:
		logger.error(f"Failed to load solution into notepad.py: {e}")


@cli.command()
def sync():
	"""Scrapes AoC website for your star progress."""
	logger = logging.getLogger(__name__)
	click.secho("Starting sync with Advent of Code website...", fg="yellow")
	now = datetime.datetime.now(datetime.timezone.utc)
	latest_year_to_check = now.year if now.month == 12 else now.year - 1
	full_progress = {}
	click.echo("Fetching star progress for each year...")
	all_years = list(range(2015, latest_year_to_check + 1))
	for year in all_years:
		try:
			year_progress = _utils.scrape_year_progress(year)
			if year_progress:
				full_progress[str(year)] = year_progress
				logger.info(f"Successfully synced progress for {year}.")
		except Exception as e:
			logger.error(f"Failed to sync progress for year {year}: {e}")
	data_to_save = {"progress": full_progress}
	with open(_utils.PROGRESS_JSON_PATH, "w") as f:
		json.dump(data_to_save, f, indent=2, sort_keys=True)
	click.secho("\n✅ Sync complete!", fg="green")


@cli.command()
def stats():
	"""Displays your puzzle completion stats in a table."""
	if not _utils.PROGRESS_JSON_PATH.exists():
		click.secho("No progress data found. Please run 'aoc sync' first.", fg="red")
		return
	with open(_utils.PROGRESS_JSON_PATH, "r") as f:
		progress_data = json.load(f).get("progress", {})
	if not progress_data:
		click.secho(
			"Progress data is empty. Run 'aoc sync' to gather data.", fg="yellow"
		)
		return
	years = sorted(progress_data.keys(), reverse=True)
	headers = [click.style("Day", bold=True)] + [
		click.style(year, bold=True) for year in years
	]
	table_data = []
	for day in range(1, 26):
		row = [f"{day}"]
		for year in years:
			stars = progress_data.get(year, {}).get(str(day), 0)
			if stars == 2:
				symbol = click.style("★★", fg="yellow")
			elif stars == 1:
				symbol = click.style("★ ", fg="bright_black")
			else:
				symbol = "  "
			row.append(symbol)
		table_data.append(row)
	click.echo(
		tabulate(table_data, headers=headers, tablefmt="psql", stralign="center")
	)


@cli.command()
@click.argument("name", default="default", required=False)
@click.option(
	"-f", "--force", is_flag=True, help="Force overwrite of notepad.py if not empty."
)
def start(name, force):
	"""Populates notepad.py with a template."""
	ctx = click.get_current_context()
	ctx.invoke(template_group.commands["load"], name=name, force=force)


@cli.command()
def clear():
	"""Clears all content from the notepad.py file."""
	aoc.clear()
	click.secho("✅ notepad.py has been cleared.", fg="green")


@cli.command(name="list")
def solutions_list():
	"""Lists all archived solutions."""
	if not _utils.SOLUTIONS_DIR.exists():
		click.echo("No solutions directory found.")
		return
	solution_files = sorted(_utils.SOLUTIONS_DIR.glob("**/part_*.py"), reverse=True)
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


def _display_perf_results(results):
	"""Helper to display performance tables."""
	click.secho("\n\n--- Performance Results ---", bold=True)
	headers = [
		click.style("Year", bold=True),
		click.style("Day", bold=True),
		click.style("Part", bold=True),
		click.style("Time (ms)", bold=True),
	]
	table_data = [[r["year"], r["day"], r["part"], f"{r['time']:.2f}"] for r in results]
	click.echo(tabulate(table_data, headers=headers, tablefmt="psql"))

	if results:
		times = [r["time"] for r in results]
		stats_data = [
			("Solutions Benchmarked", len(times)),
			("Average Time (ms)", f"{statistics.mean(times):.2f}"),
			("Median Time (ms)", f"{statistics.median(times):.2f}"),
			("Min Time (ms)", f"{min(times):.2f}"),
			("Max Time (ms)", f"{max(times):.2f}"),
			(
				"Standard Deviation",
				f"{statistics.stdev(times):.2f}" if len(times) > 1 else "N/A",
			),
		]
		click.secho("\n--- Summary Statistics ---", bold=True)
		click.echo(tabulate(stats_data, headers=["Metric", "Value"], tablefmt="psql"))


@cli.command()
@click.option(
	"--force", is_flag=True, help="Ignore the cache and re-run all benchmarks."
)
@click.option(
	"--timeout",
	type=int,
	default=None,
	help="Timeout in seconds for each solution run.",
)
def perf(force, timeout):
	"""
	Runs all saved solutions and measures their performance.
	Results are cached. Use --force to re-run.
	"""
	logger = logging.getLogger(__name__)

	if not force and _utils.PERF_CACHE_PATH.exists():
		click.secho("--- Loading Performance Results from Cache ---", bold=True)
		with open(_utils.PERF_CACHE_PATH, "r") as f:
			results = json.load(f)
		_display_perf_results(results)
		click.echo("\nUse --force to re-run benchmarks.")
		return

	click.secho("--- Running Performance Benchmark ---", bold=True)
	solution_files = sorted(_utils.SOLUTIONS_DIR.glob("**/part_*.py"))
	if not solution_files:
		click.secho("No solutions found to benchmark.", fg="yellow")
		return

	results = []
	time_regex = re.compile(r"Execution time: ([\d.]+) ms")
	env = os.environ.copy()
	env["AOC_TIME_IT"] = "true"

	with click.progressbar(solution_files, label="Benchmarking solutions") as bar:
		for path in bar:
			try:
				year = int(path.parts[-3])
				day = int(path.parts[-2])
				part_str = path.stem
			except (IndexError, ValueError):
				logger.warning(f"Could not parse year/day from path: {path}. Skipping.")
				continue

			_utils.write_context(year, day)
			try:
				result = subprocess.run(
					["python", str(path)],
					capture_output=True,
					text=True,
					env=env,
					check=False,
					timeout=timeout,
				)
				if result.returncode != 0:
					logger.error(
						f"Solution {year}-{day:02d} {part_str} failed. "
						f"Error:\n{result.stderr}"
					)
					continue
				match = time_regex.search(result.stdout)
				if match:
					results.append(
						{
							"year": year,
							"day": day,
							"part": part_str.split("_")[1],
							"time": float(match.group(1)),
						}
					)
				else:
					logger.warning(
						f"Could not parse execution time for {path}. Skipping."
					)
			except subprocess.TimeoutExpired:
				logger.warning(
					f"Solution {year}-{day:02d} {part_str} timed out after "
					f"{timeout}s. Skipping."
				)
			except Exception as e:
				logger.error(f"An unexpected error occurred while running {path}: {e}")

	# Save results to cache
	with open(_utils.PERF_CACHE_PATH, "w") as f:
		json.dump(results, f, indent=2)

	if not results:
		click.secho("\nNo solutions could be benchmarked.", fg="red")
		return

	_display_perf_results(results)


def _draw_ascii_barchart(data, title):
	"""Helper to draw a simple ASCII bar chart."""
	click.secho(f"\n--- {title} ---", bold=True)

	labels = [item[0] for item in data]
	values = [item[1] for item in data]

	if not values:
		click.echo("No data to plot.")
		return

	max_val = max(values)
	max_label_len = max(len(str(label)) for label in labels)
	bar_width = 40

	for label, val in data:
		bar_len = int((val / max_val) * bar_width) if max_val > 0 else 0
		bar = "█" * bar_len
		click.echo(f"{str(label).ljust(max_label_len)} | {val:8.2f} ms | {bar}")


@cli.command()
def plot():
	"""Displays a plot of the cached performance data."""
	if not _utils.PERF_CACHE_PATH.exists():
		click.secho("Performance cache not found.", fg="red")
		click.echo("Please run 'aoc perf' first to generate performance data.")
		return

	with open(_utils.PERF_CACHE_PATH, "r") as f:
		results = json.load(f)

	if not results:
		click.secho("No performance data found in cache.", fg="yellow")
		return

	# Aggregate data: Average time per year
	yearly_times = collections.defaultdict(list)
	for res in results:
		yearly_times[str(res["year"])].append(res["time"])

	avg_times_per_year = []
	for year, times in sorted(yearly_times.items()):
		avg_times_per_year.append((year, statistics.mean(times)))

	_draw_ascii_barchart(
		avg_times_per_year, "Performance Profile: Average Time per Year"
	)


@cli.command()
@click.option(
	"--all", "clear_all", is_flag=True, help="Clear all data without prompting."
)
def rm(clear_all):
	"""
	Clears cached data, logs, and other generated files.
	Launches an interactive prompt to select what to clear.
	Use --all to clear everything non-interactively.
	"""
	selected_ids = []

	if not clear_all:
		click.echo("Select items to clear. (e.g., '1,3,5' or 'all')")
		for i, (display_name, _, _) in enumerate(_utils.CLEARABLE_ITEMS, 1):
			click.echo(f"  {click.style(str(i), fg='yellow')}: {display_name}")

		choice_str = click.prompt(
			"\nEnter the numbers of items to clear, separated by commas"
		)

		if choice_str.lower().strip() == "all":
			clear_all = True
		else:
			id_map = {i: item[1] for i, item in enumerate(_utils.CLEARABLE_ITEMS, 1)}
			try:
				indices = [int(i.strip()) for i in choice_str.split(",") if i.strip()]
				for i in indices:
					if i in id_map and id_map[i] not in selected_ids:
						selected_ids.append(id_map[i])
			except ValueError:
				click.secho(
					"Invalid input. Please enter numbers separated by commas.", fg="red"
				)
				return

	if clear_all:
		click.secho(
			"You are about to permanently delete all cached data, logs, "
			"solutions, and configs.",
			fg="red",
			bold=True,
		)
		if not click.confirm("Are you absolutely sure you want to proceed?"):
			click.echo("Clear operation cancelled.")
			return
		all_item_ids = [item[1] for item in _utils.CLEARABLE_ITEMS]
		_utils.perform_clear(all_item_ids)
		return

	if not selected_ids:
		click.echo("No valid items selected. Operation cancelled.")
		return

	click.echo("\nYou have selected the following items for deletion:")
	for display_name, internal_id, _ in _utils.CLEARABLE_ITEMS:
		if internal_id in selected_ids:
			click.secho(f"  - {display_name}", fg="yellow")

	if not click.confirm("\nAre you sure you want to permanently delete these items?"):
		click.echo("Clear operation cancelled.")
		return

	_utils.perform_clear(selected_ids)


# Register command groups
cli.add_command(context_group)
cli.add_command(template_group)
cli.add_command(test_group)


if __name__ == "__main__":
	cli()
