import logging
import os
import re
import subprocess

import click

import aoc
from aoc import _utils

# This path needs to be redefined here relative to this file's new location
NOTEPAD_PATH = _utils.PROJECT_ROOT / "notepad.py"


@click.group(name="test")
def test_group():
	"""Manages and runs test cases for puzzles."""
	pass


@test_group.command(name="add")
@click.option(
	"-p",
	"--part",
	type=click.Choice(["1", "2"]),
	prompt="Which part is this test for? (1 or 2)",
)
def test_add(part):
	"""Interactively add a new test case for the current context."""
	target_year, target_day = aoc.year, aoc.day
	part_key = f"part_{part}"

	click.echo(
		f"--- Adding New Test Case for {target_year}-{target_day} Part {part} ---"
	)
	test_input = click.edit()
	if test_input is None:
		click.echo("No input provided. Aborting.")
		return
	test_output = click.prompt("What is the expected output?")

	tests_data = _utils._read_tests_cache(target_year, target_day)
	tests_data[part_key].append(
		{"input": test_input.strip(), "output": test_output.strip()}
	)
	_utils._write_tests_cache(target_year, target_day, tests_data)
	click.secho("\n✅ Test case added successfully!", fg="green")


@test_group.command(name="list")
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
				click.secho(f"  Test #{i + 1}:", bold=True)
				indented_input = "    " + "\n    ".join(test["input"].splitlines())
				click.secho(f"    --- Input ---\n{indented_input}", fg="bright_black")
				click.echo(f"    --- Expected Output ---\n    {test['output']}")


@test_group.command(name="delete")
@click.argument("part", type=click.Choice(["1", "2"]))
@click.argument("index", type=int)
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


@test_group.command(name="run")
def test_run():
	"""Runs notepad.py against all saved tests for the current context."""
	logger = logging.getLogger(__name__)
	target_year, target_day = aoc.year, aoc.day

	try:
		notepad_content = NOTEPAD_PATH.read_text()
		part_match = re.search(
			r"aoc\.submit\s*\(\s*[^,]+,\s*part\s*=\s*([12])\s*\)", notepad_content
		)
		if not part_match:
			part_match = re.search(
				r"aoc\.bind\s*\(\s*part\s*=\s*([12])\s*\)", notepad_content
			)

		if not part_match:
			click.secho("Error: Could not determine part from notepad.py.", fg="red")
			click.secho(
				"Hint: Make sure you have an `aoc.submit(answer, part=1)` "
				"or `aoc.bind(part=1)` call.",
				fg="red",
			)
			return
		part = int(part_match.group(1))
		part_key = f"part_{part}"
	except FileNotFoundError:
		click.secho("Error: notepad.py not found.", fg="red")
		return

	tests_data = _utils._read_tests_cache(target_year, target_day)
	tests_to_run = tests_data.get(part_key, [])
	if not tests_to_run:
		click.echo(f"No test cases found for Part {part}. Add one with 'aoc test add'.")
		return

	click.secho(
		f"--- Running {len(tests_to_run)} Test(s) for Part {part} ---", bold=True
	)
	passed_count = 0

	for i, test in enumerate(tests_to_run):
		click.secho(f"\n--- Test Case #{i + 1} ---", fg="yellow")
		test_env = os.environ.copy()
		test_env["AOC_TEST_MODE"] = "true"
		test_env["AOC_TEST_INPUT"] = test["input"]
		test_env["AOC_TEST_OUTPUT"] = test["output"]

		try:
			result = subprocess.run(
				["python", NOTEPAD_PATH], capture_output=True, text=True, env=test_env
			)
			output = result.stdout.strip()
			click.echo(output)
			if result.stderr:
				click.secho(result.stderr.strip(), fg="red")
			if "✅ PASSED" in output:
				passed_count += 1
		except Exception as e:
			logger.error(f"An unexpected error occurred running test #{i + 1}: {e}")

	color = "green" if passed_count == len(tests_to_run) else "red"
	click.secho(
		f"\n--- Summary ---\n{passed_count} / {len(tests_to_run)} tests passed.",
		fg=color,
		bold=True,
	)
