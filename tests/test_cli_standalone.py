import json

from click.testing import CliRunner

import aoc
from aoc import _utils
from aoc.cli import cli


def test_load_command(monkeypatch, tmp_path):
	"""Tests the `aoc load` command."""
	runner = CliRunner()

	# Arrange: Create a fake solutions directory and a fake solution file
	fake_solutions_dir = tmp_path / "solutions"
	fake_solution_path = fake_solutions_dir / "2025" / "01"
	fake_solution_path.mkdir(parents=True)
	solution_content = "# My brilliant solution"
	(fake_solution_path / "part_1.py").write_text(solution_content)

	# Create a fake notepad to be overwritten
	fake_notepad_path = tmp_path / "notepad.py"
	fake_notepad_path.write_text("# initial content")

	# Patch the paths in the _utils module, where they are now defined
	monkeypatch.setattr(_utils, "SOLUTIONS_DIR", fake_solutions_dir)
	monkeypatch.setattr(_utils, "NOTEPAD_PATH", fake_notepad_path)
	monkeypatch.setattr(aoc, "year", 2025)
	monkeypatch.setattr(aoc, "day", 1)

	# Act
	result = runner.invoke(cli, ["load", "1"], input="y\n")

	# Assert
	assert result.exit_code == 0
	assert "Successfully loaded Part 1" in result.output
	assert fake_notepad_path.read_text() == solution_content


def test_sync_command(monkeypatch, tmp_path, requests_mock):
	"""Tests the `aoc sync` command."""
	runner = CliRunner()

	# Arrange
	# Mock the network call to the AoC calendar page
	mock_html = """
	<pre class="calendar">
	<a href="/2025/day/1" aria-label="Day 1, two stars">  1 <span class="calendar-day">1</span></a>
	<a href="/2025/day/2" aria-label="Day 2, one star">  2 <span class="calendar-day">2</span></a>
	</pre>
	"""  # noqa: E501
	# Mock requests for all years that will be checked (2015-2025)
	for year in range(2015, 2026):
		if year == 2025:
			requests_mock.get(f"https://adventofcode.com/{year}", text=mock_html)
		else:
			requests_mock.get(f"https://adventofcode.com/{year}", text="")

	# Patch the paths and session cookie
	fake_progress_path = tmp_path / "progress.json"
	monkeypatch.setattr(_utils, "PROGRESS_JSON_PATH", fake_progress_path)
	monkeypatch.setattr(_utils, "get_session_cookie", lambda: "fake_cookie")
	# Mock the current date so we know which years to sync
	monkeypatch.setattr(_utils, "get_latest_puzzle_date", lambda: (2025, 25))

	# Act
	result = runner.invoke(cli, ["sync"])

	# Assert
	assert result.exit_code == 0
	assert "Sync complete!" in result.output
	assert fake_progress_path.exists()
	with open(fake_progress_path, "r") as f:
		data = json.load(f)
	assert data["progress"]["2025"]["1"] == 2
	assert data["progress"]["2025"]["2"] == 1
