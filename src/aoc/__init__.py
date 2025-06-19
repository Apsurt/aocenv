import logging
import re
import os
import time
from contextlib import contextmanager
from typing import Union

import click

from . import _utils
from .parsers import InputParser
from . import tools

__all__ = [
	"get_input",
	"get_input_parser",
	"get_instructions",
	"submit",
	"bind",
	"clear",
	"timed",
	"tools",
	"year",
	"day",
]

# --- Test Mode Initialization ---
TEST_MODE = os.getenv("AOC_TEST_MODE") == "true"
_test_input_data = os.getenv("AOC_TEST_INPUT")
_test_expected_answer = os.getenv("AOC_TEST_OUTPUT")

# --- CONTEXT DETERMINATION ---
context: Union[tuple[int, int], None] = _utils.read_context()
if context:
	year, day = context
	logging.getLogger(__name__).info(f"Using persisted context: Year {year}, Day {day}")
else:
	year, day = _utils.get_latest_puzzle_date()
	logging.getLogger(__name__).info("No context set. Defaulting to latest puzzle.")


# --- PUBLIC FUNCTIONS ---
def get_instructions() -> str:
	"""
	Gets the puzzle instructions for the current context (year, day).

	Returns:
		A formatted string of the puzzle instructions for the terminal.
	"""
	return _utils.get_aoc_data(year, day, data_type="instructions")


def get_input_parser() -> InputParser:
	"""
	Returns a fluent InputParser object for advanced input processing.
	"""
	return InputParser(get_input())


def get_input() -> str:
	"""
	Gets the puzzle input for the current context (year, day).
	In Test Mode, this returns the example input instead.
	"""
	logger = logging.getLogger(__name__)
	if TEST_MODE:
		logger.info("TEST MODE: Returning example input.")
		return _test_input_data if _test_input_data is not None else ""

	return _utils.get_aoc_data(year, day, data_type="input")


def submit(answer, part: int) -> str:
	"""

	Submits an answer for the current puzzle context.
	The puzzle part (1 or 2) must be provided.
	In Test Mode, this performs a local check against the expected answer.
	"""
	logger = logging.getLogger(__name__)

	if TEST_MODE:
		logger.info(
			f"TEST MODE: Checking answer '{answer}' against "
			f"expected '{_test_expected_answer}'."
		)
		str_answer = str(answer)
		str_expected = str(_test_expected_answer)

		if str_answer == str_expected:
			return "✅ PASSED"
		else:
			return (
				f"❌ FAILED: Got '{str_answer}', but expected '{_test_expected_answer}'"
			)

	if part not in [1, 2]:
		err_msg = "The 'part' argument for submit() must be 1 or 2."
		logger.error(err_msg)
		return err_msg

	response_text = _utils.post_answer(year, day, part, answer)

	if "That's the right answer!" in response_text:
		logger.info("Answer is correct!")
		if _utils.get_bool_config_setting("auto_bind", default=True):
			logger.info(f"Auto-binding solution for Part {part}...")
			bind(part)
		return f"✅ {response_text}"

	elif "You don't seem to be solving the right level" in response_text:
		logger.warning(f"Part {part} has already been completed.")
		return (
			f"✅ Part {part} has already been completed. The server did not "
			"accept the new submission."
		)

	else:
		logger.warning(f"Answer is incorrect. Response: {response_text}")
		return f"❌ {response_text}"


def bind(part: int, overwrite: bool = False):
	"""
	Archives the code from notepad.py to the solutions directory.
	The puzzle part (1 or 2) must be provided.
	The 'aoc.bind()' call is automatically removed from the saved code.
	"""
	logger = logging.getLogger(__name__)
	if part not in [1, 2]:
		logger.error("The 'part' argument for bind() must be 1 or 2.")
		return

	source_path = _utils.NOTEPAD_PATH
	dest_dir = _utils.SOLUTIONS_DIR / str(year) / f"{day:02d}"
	dest_path = dest_dir / f"part_{part}.py"

	logger.info(f"Binding solution for {year}-{day} Part {part}...")

	if not source_path.exists():
		logger.error("notepad.py not found!")
		return

	if dest_path.exists() and not overwrite:
		logger.warning(
			f"Solution already exists at {dest_path}. "
			f"Use bind(overwrite=True, part={part}) to replace it."
		)
		return

	try:
		content = source_path.read_text()
		bind_pattern = re.compile(r"^\s*aoc\.bind\s*\(.*\)\s*$", re.MULTILINE)
		cleaned_content = re.sub(bind_pattern, "", content).rstrip()

		dest_dir.mkdir(parents=True, exist_ok=True)
		dest_path.write_text(cleaned_content)
		logger.info(f"Solution successfully saved to {dest_path}")

		if _utils.get_bool_config_setting("auto_commit_on_bind"):
			_utils.git_commit_solution(year, day, part)

		if _utils.get_bool_config_setting("auto_clear_on_bind"):
			logger.info("Auto-clearing notepad.py...")
			clear()

	except Exception as e:
		logger.error(f"Failed to bind solution: {e}")


def clear():
	"""Clears all content from the notepad.py file."""
	logger = logging.getLogger(__name__)
	if _utils.NOTEPAD_PATH.exists():
		_utils.NOTEPAD_PATH.write_text("")
		logger.info("notepad.py has been cleared.")


@contextmanager
def timed():
	"""A context manager to time code, activated by `aoc run -t`."""
	should_time = os.getenv("AOC_TIME_IT") == "true"
	start_time = 0

	if should_time:
		start_time = time.perf_counter()

	try:
		yield
	finally:
		if should_time:
			end_time = time.perf_counter()
			duration_ms = (end_time - start_time) * 1000
			click.secho(f"\n⏱️  Execution time: {duration_ms:.2f} ms", fg="yellow")
