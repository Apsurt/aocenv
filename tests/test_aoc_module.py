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

	# Act
	result = aoc.submit("any_answer", part=1)

	# Assert
	assert "✅ That's the right answer!" in result
