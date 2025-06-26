import pytest

import aoc
from aoc import _utils

# --- Tests for get_input() ---


def test_get_input_normal_mode(monkeypatch):
	"""Tests that get_input calls the utility function in normal mode."""
	# Arrange: Mock the backend utility function to see if it gets called
	monkeypatch.setattr(_utils, "get_aoc_data", lambda y, d, data_type: "real_input")
	# Ensure we are not in TEST_MODE
	monkeypatch.setattr(aoc, "TEST_MODE", False)

	# Act
	result = aoc.get_input()

	# Assert
	assert result == "real_input"


def test_get_input_test_mode(monkeypatch):
	"""Tests that get_input returns the test data in test mode."""
	# Arrange: Set the test mode variables
	monkeypatch.setattr(aoc, "TEST_MODE", True)
	monkeypatch.setattr(aoc, "_test_input_data", "test_input")

	# Act
	result = aoc.get_input()

	# Assert
	assert result == "test_input"


# --- Tests for submit() ---


@pytest.mark.parametrize(
	"answer, expected_output, should_pass",
	[
		("123", "123", True),  # Correct answer
		("456", "123", False),  # Incorrect answer
	],
)
def test_submit_test_mode(monkeypatch, answer, expected_output, should_pass):
	"""Tests that submit() correctly validates answers in test mode."""
	# Arrange
	monkeypatch.setattr(aoc, "TEST_MODE", True)
	monkeypatch.setattr(aoc, "_test_expected_answer", expected_output)

	# Act
	result = aoc.submit(answer, part=1)

	# Assert
	if should_pass:
		assert "✅ PASSED" in result
	else:
		assert "❌ FAILED" in result


def test_submit_normal_mode(monkeypatch):
	"""Tests that submit() calls the post_answer utility in normal mode."""
	# Arrange
	monkeypatch.setattr(aoc, "TEST_MODE", False)
	# Mock the backend function and the config check to isolate the submit logic
	monkeypatch.setattr(
		_utils, "post_answer", lambda y, d, p, a: "✅ That's the right answer!"
	)
	monkeypatch.setattr(_utils, "get_bool_config_setting", lambda key, default: False)
	monkeypatch.setattr(
		_utils, "read_progress_file", lambda: {"progress": {}}
	)  # Ensure not marked as completed

	# Act
	result = aoc.submit("any_answer", part=1)

	# Assert
	assert "✅ That's the right answer!" in result


def test_submit_already_completed_correct_answer(monkeypatch):
	"""Tests submit() when puzzle is already completed and new answer is correct."""
	# Arrange
	monkeypatch.setattr(aoc, "TEST_MODE", False)
	monkeypatch.setattr(aoc, "year", 2025)
	monkeypatch.setattr(aoc, "day", 1)
	# Simulate puzzle being completed (2 stars for day 1)
	monkeypatch.setattr(
		_utils, "read_progress_file", lambda: {"progress": {"2025": {"1": 2}}}
	)
	# Mock scraping to return a known correct answer
	monkeypatch.setattr(
		_utils,
		"scrape_day_page_for_answers",
		lambda y, d: {1: "known_correct_part1", 2: "known_correct_part2"},
	)
	# Ensure post_answer is NOT called
	monkeypatch.setattr(
		_utils,
		"post_answer",
		lambda *args, **kwargs: pytest.fail("post_answer should not be called"),
	)

	# Act
	result = aoc.submit("known_correct_part1", part=1)

	# Assert
	assert "✅ Your answer 'known_correct_part1' is correct!" in result


def test_submit_already_completed_incorrect_answer(monkeypatch):
	"""Tests submit() when puzzle is already completed and new answer is incorrect."""
	# Arrange
	monkeypatch.setattr(aoc, "TEST_MODE", False)
	monkeypatch.setattr(aoc, "year", 2025)
	monkeypatch.setattr(aoc, "day", 1)
	# Simulate puzzle being completed (2 stars for day 1)
	monkeypatch.setattr(
		_utils, "read_progress_file", lambda: {"progress": {"2025": {"1": 2}}}
	)
	# Mock scraping to return a known correct answer
	monkeypatch.setattr(
		_utils,
		"scrape_day_page_for_answers",
		lambda y, d: {1: "known_correct_part1", 2: "known_correct_part2"},
	)
	# Ensure post_answer is NOT called
	monkeypatch.setattr(
		_utils,
		"post_answer",
		lambda *args, **kwargs: pytest.fail("post_answer should not be called"),
	)

	# Act
	result = aoc.submit("wrong_answer", part=1)

	# Assert
	assert (
		"❌ Your answer 'wrong_answer' is incorrect. The correct answer was 'known_correct_part1'." #noqa E501
		in result
	)


def test_submit_already_completed_no_scraped_answer(monkeypatch):
	"""Tests submit() when puzzle is completed but correct answer cannot be scraped."""
	# Arrange
	monkeypatch.setattr(aoc, "TEST_MODE", False)
	monkeypatch.setattr(aoc, "year", 2025)
	monkeypatch.setattr(aoc, "day", 1)
	# Simulate puzzle being completed (2 stars for day 1)
	monkeypatch.setattr(
		_utils, "read_progress_file", lambda: {"progress": {"2025": {"1": 2}}}
	)
	# Mock scraping to return no answers
	monkeypatch.setattr(_utils, "scrape_day_page_for_answers", lambda y, d: {})
	# Ensure post_answer is NOT called
	monkeypatch.setattr(
		_utils,
		"post_answer",
		lambda *args, **kwargs: pytest.fail("post_answer should not be called"),
	)

	# Act
	result = aoc.submit("any_answer", part=1)

	# Assert
	assert (
		"⚠️ Puzzle already completed, but could not verify answer against AoC website."
		in result
	)
