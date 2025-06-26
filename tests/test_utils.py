from aoc import _utils


# The 'monkeypatch' and 'tmp_path' fixtures are provided by pytest automatically.
def test_read_and_write_context(monkeypatch, tmp_path):
	"""Tests that we can write to and read from the context file."""
	# Use the tmp_path fixture for our test file
	fake_context_path = tmp_path / ".context.json"

	# Use monkeypatch to temporarily change the path in the _utils module
	monkeypatch.setattr(_utils, "CONTEXT_FILE_PATH", fake_context_path)

	# Act
	_utils.write_context(2025, 99)
	context = _utils.read_context()

	# Assert
	assert fake_context_path.exists()
	assert context == (2025, 99)


# The 'requests_mock' fixture comes from the pytest-requests-mock library
def test_get_aoc_data_from_web(monkeypatch, tmp_path, requests_mock):
	"""Tests fetching data from the web when it's not in the cache."""
	# Arrange
	# Point our cache to the temporary directory
	monkeypatch.setattr(_utils, "CACHE_DIR", tmp_path)
	# Mock the network request to the AoC website
	requests_mock.get("https://adventofcode.com/2025/day/1/input", text="mocked input")
	# Mock the session cookie to prevent ConnectionError
	monkeypatch.setattr(_utils, "get_session_cookie", lambda: "fake_cookie")

	# Act
	data = _utils.get_aoc_data(2025, 1, "input")

	# Assert
	assert data == "mocked input"
	# Check that the data was saved to our temporary cache
	cached_file = tmp_path / "2025" / "01" / "input.txt"
	assert cached_file.exists()
	assert cached_file.read_text() == "mocked input"


def test_post_answer(monkeypatch, requests_mock):
	"""Tests submitting an answer and parsing the response."""
	# Arrange
	# Mock the POST request and the HTML response from the server
	mock_html = "<article><p>That's the right answer!</p></article>"
	requests_mock.post("https://adventofcode.com/2025/day/1/answer", text=mock_html)
	# Mock the session cookie to prevent ConnectionError
	monkeypatch.setattr(_utils, "get_session_cookie", lambda: "fake_cookie")

	# Act
	response = _utils.post_answer(2025, 1, 1, "my_answer")

	# Assert
	assert response == "That's the right answer!"
