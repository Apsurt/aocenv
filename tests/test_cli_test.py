import json
import click
from click.testing import CliRunner

from aoc.cli import cli
from aoc import _utils
import aoc


def test_test_command_lifecycle(monkeypatch, tmp_path):
	"""
	Tests the full lifecycle of the `aoc test` command group:
	add, list, run, and delete.
	"""
	runner = CliRunner()

	# 1. Arrange: Create a fake project and cache environment
	fake_cache_dir = tmp_path / ".cache"
	fake_cache_dir.mkdir()
	monkeypatch.setattr(_utils, "CACHE_DIR", fake_cache_dir)

	# Directly patch the global year and day in the aoc module for this test.
	monkeypatch.setattr(aoc, "year", 2025)
	monkeypatch.setattr(aoc, "day", 1)

	# Create a fake notepad.py for the test runner to execute
	fake_notepad_path = tmp_path / "notepad.py"
	fake_notepad_path.write_text(
		"""
import aoc
puzzle_input = aoc.get_input()
answer = puzzle_input.count('x')
print(aoc.submit(answer, part=1))
"""
	)
	# The test command module needs to know where our fake notepad is
	from aoc.cli_commands import test as test_cli

	monkeypatch.setattr(test_cli, "NOTEPAD_PATH", fake_notepad_path)

	# Mock click.edit() so it doesn't hang waiting for an editor.
	monkeypatch.setattr(click, "edit", lambda: "xxxyy")

	# 2. Act & Assert: Add a new test case
	add_input = "1\n3\n"  # Part 1, expected output is '3'
	result_add = runner.invoke(cli, ["test", "add"], input=add_input)

	assert result_add.exit_code == 0
	assert "Test case added successfully" in result_add.output

	# Verify the tests.json file was created correctly
	test_cache_file = fake_cache_dir / "2025" / "01" / "tests.json"
	assert test_cache_file.exists()
	with open(test_cache_file, "r") as f:
		test_data = json.load(f)
	assert test_data["part_1"][0]["input"] == "xxxyy"
	assert test_data["part_1"][0]["output"] == "3"

	# 3. Act & Assert: List the tests
	result_list = runner.invoke(cli, ["test", "list"])
	assert result_list.exit_code == 0
	assert "Test Cases for 2025-01" in result_list.output
	assert "xxxyy" in result_list.output

	# 4. Act & Assert: Run the tests
	result_run = runner.invoke(cli, ["test", "run"])
	assert result_run.exit_code == 0
	assert "✅ PASSED" in result_run.output
	assert "1 / 1 tests passed" in result_run.output

	# 5. Act & Assert: Delete the test
	result_delete = runner.invoke(cli, ["test", "delete", "1", "1"], input="y\n")
	assert result_delete.exit_code == 0
	assert "Test #1 for Part 1 has been deleted" in result_delete.output
	with open(test_cache_file, "r") as f:
		test_data_after_delete = json.load(f)
	assert not test_data_after_delete["part_1"]
