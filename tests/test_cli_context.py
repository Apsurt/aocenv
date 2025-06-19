import json

from click.testing import CliRunner

from aoc import _utils
from aoc.cli import cli


def test_context_set_valid_date(monkeypatch, tmp_path):
	"""Tests that `aoc context set` works for a valid date."""
	# Arrange
	runner = CliRunner()
	fake_context_path = tmp_path / ".context.json"
	monkeypatch.setattr(_utils, "CONTEXT_FILE_PATH", fake_context_path)
	# Mock the latest available date to be the end of 2023
	monkeypatch.setattr(_utils, "get_latest_puzzle_date", lambda: (2023, 25))

	# Act
	result = runner.invoke(cli, ["context", "set", "--year", "2023", "--day", "15"])

	# Assert
	assert result.exit_code == 0
	assert "Context set to Year 2023, Day 15" in result.output
	assert json.loads(fake_context_path.read_text()) == {"year": 2023, "day": 15}


def test_context_set_future_date_fails(monkeypatch):
	"""Tests that `aoc context set` fails for a date that is not yet available."""
	# Arrange
	runner = CliRunner()
	# Mock the latest available date to be Dec 12, 2025
	monkeypatch.setattr(_utils, "get_latest_puzzle_date", lambda: (2025, 12))

	# Act: Try to set the context to a future date
	result = runner.invoke(cli, ["context", "set", "--year", "2025", "--day", "14"])

	# Assert
	assert result.exit_code != 0  # Should fail
	assert "Error: Puzzle for 2025-14 is not yet available." in result.output


def test_context_set_invalid_day_fails():
	"""Tests that `aoc context set` fails for a day outside the 1-25 range."""
	# Arrange
	runner = CliRunner()

	# Act
	result = runner.invoke(cli, ["context", "set", "--year", "2022", "--day", "99"])

	# Assert
	assert result.exit_code != 0
	assert "Error: Day must be between 1 and 25." in result.output


def test_context_set_invalid_year_fails():
	"""Tests that `aoc context set` fails for a year before 2015."""
	# Arrange
	runner = CliRunner()

	# Act
	result = runner.invoke(cli, ["context", "set", "--year", "2014", "--day", "10"])

	# Assert
	assert result.exit_code != 0
	assert "Error: Year must be between 2015" in result.output


def test_context_clear(monkeypatch, tmp_path):
	"""Tests that `aoc context clear` removes the context file."""
	# Arrange
	runner = CliRunner()
	fake_context_path = tmp_path / ".context.json"
	monkeypatch.setattr(_utils, "CONTEXT_FILE_PATH", fake_context_path)

	# Create a dummy context file to be deleted
	fake_context_path.write_text('{"year": 2025, "day": 99}')
	assert fake_context_path.exists()

	# Act
	result = runner.invoke(cli, ["context", "clear"])

	# Assert
	assert result.exit_code == 0
	assert "Context cleared" in result.output
	assert not fake_context_path.exists()
