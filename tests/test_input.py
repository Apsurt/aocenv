import pytest
from unittest.mock import patch, Mock
import requests
import os
import tempfile
from pathlib import Path
from aoc.context import Context
from aoc.input import Grid, Input, get_input
from aoc.cache import get_input_cache_path, read_input_cache, write_input_cache

RAW_NUMBERS = """
1721
979
366
"""

RAW_GRID = """
..##..
#...#.
.#....
"""

RAW_PARAGRAPHS = """
1000
2000

4000

5000
6000
"""

RAW_MIXED_TYPE = "1\n2\nthree\n4"

# region Grid Tests

def test_grid_init():
    grid_data = [[1, 2], [3, 4]]
    grid = Grid(grid_data)
    assert grid.height == 2
    assert grid.width == 2
    assert grid.data == grid_data

def test_grid_init_empty():
    grid = Grid([])
    assert grid.height == 0
    assert grid.width == 0

def test_grid_get():
    grid = Grid([['a', 'b'], ['c', 'd']])
    assert grid.get(0, 0) == 'a'
    assert grid.get(1, 1) == 'd'
    assert grid.get(2, 2) is None
    assert grid.get(2, 2, default='z') == 'z'

def test_grid_neighbors():
    grid = Grid([[1, 2, 3], [4, 5, 6], [7, 8, 9]])
    # Corner
    assert grid.neighbors(0, 0) == {(1, 0): 4, (0, 1): 2}
    # Edge
    assert grid.neighbors(1, 0) == {(0, 0): 1, (2, 0): 7, (1, 1): 5}
    # Center
    assert grid.neighbors(1, 1) == {(0, 1): 2, (2, 1): 8, (1, 0): 4, (1, 2): 6}

def test_grid_neighbors_diagonals():
    grid = Grid([[1, 2, 3], [4, 5, 6], [7, 8, 9]])
    neighbors = grid.neighbors(1, 1, diagonals=True)
    assert len(neighbors) == 8
    assert neighbors[(0, 0)] == 1
    assert neighbors[(2, 2)] == 9

def test_grid_transpose():
    grid = Grid([[1, 2, 3], [4, 5, 6]])
    transposed = grid.transpose()
    assert transposed.height == 3
    assert transposed.width == 2
    assert transposed.data == [[1, 4], [2, 5], [3, 6]]

def test_grid_rows_cols():
    grid_data = [[1, 2], [3, 4]]
    grid = Grid(grid_data)
    assert list(grid.rows()) == [[1, 2], [3, 4]]
    assert list(grid.cols()) == [(1, 3), (2, 4)]

def test_grid_repr():
    grid = Grid([[1]])
    assert repr(grid) == "<Grid height=1 width=1>"

# endregion

# region Input Tests

def test_input_init():
    inp = Input("raw")
    assert inp.raw == "raw"
    assert inp.get() == "raw"

@patch("aoc.input.get_input", return_value=Input("mocked input"))
def test_input_init_fetches_input(mock_get_input):
    # Act
    inp = Input()

    # Assert
    assert inp.raw == "mocked input"
    mock_get_input.assert_called_once()


def test_input_pythonic_methods():
    inp = Input(RAW_NUMBERS).lines()
    assert len(inp) == 3
    assert inp[0] == "1721"
    assert inp[1:3] == ["979", "366"]

    items = [item for item in inp]
    assert items == ["1721", "979", "366"]

def test_input_getitem_error():
    with pytest.raises(TypeError, match="Current value of type 'str' is not subscriptable."):
        Input("raw")[0]

def test_input_strip():
    inp = Input("  hello  ").strip()
    assert inp.get() == "hello"
    inp_list = Input(["  a ", " b  "]).strip()
    assert inp_list.get() == ["a", "b"]
    inp_mixed_list = Input(["  a ", 1, " b  "]).strip()
    assert inp_mixed_list.get() == ["a", "b"]

def test_input_lines():
    inp = Input(RAW_NUMBERS).lines()
    assert inp.get() == ["1721", "979", "366"]

def test_input_paragraphs():
    inp = Input(RAW_PARAGRAPHS).paragraphs()
    assert inp.get() == ["1000\n2000", "4000", "5000\n6000"]

def test_input_split():
    # With separator
    inp_str = Input("a,b,c").split(',')
    assert inp_str.get() == ['a', 'b', 'c']
    inp_list = Input(["1-a", "2-b"]).lines().split('-')
    assert inp_list.get() == [['1', 'a'], ['2', 'b']]

    # Without separator (whitespace splitting)
    # Single spaces
    inp1 = Input("abc def").split()
    assert inp1.get() == ['abc', 'def']

    # Multiple spaces
    inp2 = Input("abc   def").split()
    assert inp2.get() == ['abc', 'def']

    # Mixed whitespace (spaces, tabs, newlines)
    inp3 = Input("abc\t   \n \t   def").split()
    assert inp3.get() == ['abc', 'def']

    # List of strings
    inp4 = Input(["1  2  3", "4\t5\t6"]).split()
    assert inp4.get() == [['1', '2', '3'], ['4', '5', '6']]

    # Leading/trailing whitespace
    inp5 = Input("  abc   def  ").split()
    assert inp5.get() == ['abc', 'def']

def test_input_map():
    inp = Input(RAW_NUMBERS).lines().map(int)
    assert inp.get() == [1721, 979, 366]
    inp_single = Input("5").map(int)
    assert inp_single.get() == 5

def test_input_filter():
    inp = Input(RAW_NUMBERS).lines().to_int().filter(lambda x: x > 1000)
    assert inp.get() == [1721]

def test_input_flatten():
    inp = Input(RAW_PARAGRAPHS).paragraphs().split('\n').flatten()
    assert inp.get() == ["1000", "2000", "4000", "5000", "6000"]

def test_input_findall():
    line = "Game 1: 3 blue, 4 red; 1 red, 2 green"
    inp_str = Input(line).findall(r'\d+')
    assert inp_str.get() == ['1', '3', '4', '1', '2']

    lines = ["pos=<1, 2>", "pos=<3, 4>"]
    inp_list = Input("\n".join(lines)).lines().findall(r'<(-?\d+), *(-?\d+)>')
    assert inp_list.flatten().map(list).get() == [['1', '2'], ['3', '4']]

def test_input_to_int():
    inp = Input(RAW_NUMBERS).lines().to_int()
    assert inp.get() == [1721, 979, 366]

    inp_nested = Input(RAW_PARAGRAPHS).paragraphs().split('\n').to_int()
    assert inp_nested.get() == [[1000, 2000], [4000], [5000, 6000]]

    inp_mixed = Input(RAW_MIXED_TYPE).lines().to_int()
    assert inp_mixed.get() == [1, 2, 'three', 4]

def test_input_to_float():
    inp = Input("1.1\n2.2").lines().to_float()
    assert inp.get() == [1.1, 2.2]

def test_input_get():
    val = Input("final").get()
    assert val == "final"

def test_input_grid():
    # From string
    grid1 = Input(RAW_GRID).grid()
    assert grid1.height == 3
    assert grid1.width == 6
    assert grid1.get(0, 2) == '#'

    # From list of strings
    grid2 = Input(RAW_GRID).lines().grid()
    assert grid2.height == 3
    assert grid2.width == 6
    assert grid2.get(1, 0) == '#'

    # From list of lists
    grid3 = Input(RAW_GRID).lines().map(list).grid()
    assert grid3.height == 3
    assert grid3.width == 6
    assert grid3.get(2, 1) == '#'

    with pytest.raises(TypeError):
        Input(123).grid()

def test_input_chaining():
    result = (
        Input(RAW_PARAGRAPHS)
        .paragraphs()
        .split('\n')
        .to_int()
        .map(sum)
        .filter(lambda x: x > 4000)
        .get()
    )
    assert result == [11000]

# endregion

def _read_test_input_file(year: int, day: int) -> str:
    """Helper to read content from a test input file."""
    current_dir = os.path.dirname(__file__)
    file_path = os.path.join(current_dir, f"{year}_{day}.txt")
    with open(file_path, 'r') as f:
        return f.read()


# region Custom Input Tests

def test_input_2017_day_09():
    raw_input = _read_test_input_file(2017, 9)
    inp = Input(raw_input)

    # Use findall to extract all garbage sections (including < and >)
    garbage_sections = inp.findall(r'<[^>]*>').get()
    assert len(garbage_sections) == 1756

    # Use findall to count all opening braces
    opening_braces = inp.findall(r'{').get()
    assert len(opening_braces) == 1756

def test_input_2024_day_15():
    raw_input = _read_test_input_file(2024, 15)
    inp = Input(raw_input)

    # The input has a grid and then a line of directions
    parts = inp.lines().get()
    grid_str = "\n".join(parts[:-1])
    directions_str = parts[-1]

    # Test grid parsing
    grid = Input(grid_str).grid()
    assert grid.height == 69
    assert grid.width == 50
    assert grid.get(0, 0) == '#'
    assert grid.get(24, 24) == '@'

    # Test directions parsing
    directions = Input(directions_str).findall(r'[<>^v]').get()
    assert len(directions) == 1000
    assert directions[0] == 'v'
    assert directions[-1] == '<'

# endregion

# region get_input Tests

@patch("requests.get")
def test_get_input_success(mock_get):
    # Arrange
    ctx = Context(year=2025, day=1, part=1)
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.text = "mocked input"
    mock_get.return_value = mock_response

    with patch("aoc.input.get_session_cookies", return_value={"session": "mock_token"}):
        with patch("aoc.input.read_input_cache", return_value=None):
            with patch("aoc.input.write_input_cache"):
                # Act
                result = get_input(ctx)

                # Assert
                assert isinstance(result, Input)
                assert result.raw == "mocked input"
                mock_get.assert_called_once_with(
                    "https://adventofcode.com/2025/day/1/input",
                    cookies={"session": "mock_token"},
                )

@patch("requests.get")
def test_get_input_failure(mock_get):
    # Arrange
    ctx = Context(year=2025, day=1, part=1)
    mock_get.side_effect = requests.exceptions.RequestException("mock error")

    with patch("aoc.input.get_session_cookies", return_value={"session": "mock_token"}):
        with patch("aoc.input.read_input_cache", return_value=None):
            # Act & Assert
            with pytest.raises(RuntimeError, match="Failed to fetch input: mock error"):
                get_input(ctx)

def test_get_input_no_token():
    # Arrange
    ctx = Context(year=2025, day=1, part=1)
    with patch("aoc.input.get_session_cookies", return_value=None):
        # Act & Assert
        with pytest.raises(ValueError, match="Session cookie is not set."):
            get_input(ctx)

# endregion

# region Cache Tests

def test_get_input_cache_path():
    # Arrange
    ctx = Context(year=2024, day=5, part=1)
    cookies = {"session": "test_session_token"}

    # Act
    cache_path = get_input_cache_path(ctx, cookies)

    # Assert
    assert ".aoc_cache" in str(cache_path)
    assert "2024" in str(cache_path)
    assert "inputs" in str(cache_path)
    assert cache_path.name == "day5.txt"

def test_get_input_cache_path_different_sessions():
    # Arrange
    ctx = Context(year=2024, day=5, part=1)
    cookies1 = {"session": "session_token_1"}
    cookies2 = {"session": "session_token_2"}

    # Act
    cache_path1 = get_input_cache_path(ctx, cookies1)
    cache_path2 = get_input_cache_path(ctx, cookies2)

    # Assert - Different sessions should have different cache paths
    assert cache_path1 != cache_path2
    assert cache_path1.parent.parent.parent != cache_path2.parent.parent.parent

def test_write_and_read_input_cache():
    # Arrange
    ctx = Context(year=2024, day=10, part=1)
    cookies = {"session": "test_token"}
    test_content = "test puzzle input\nwith multiple lines"

    with tempfile.TemporaryDirectory() as tmpdir:
        with patch("pathlib.Path.home", return_value=Path(tmpdir)):
            # Act - Write cache
            write_input_cache(ctx, cookies, test_content)

            # Assert - Cache file exists
            cache_path = get_input_cache_path(ctx, cookies)
            assert cache_path.exists()

            # Act - Read cache
            cached_content = read_input_cache(ctx, cookies)

            # Assert - Content matches
            assert cached_content == test_content

def test_read_input_cache_not_exists():
    # Arrange
    ctx = Context(year=2099, day=99, part=1)
    cookies = {"session": "test_token"}

    with tempfile.TemporaryDirectory() as tmpdir:
        with patch("pathlib.Path.home", return_value=Path(tmpdir)):
            # Act
            cached_content = read_input_cache(ctx, cookies)

            # Assert
            assert cached_content is None

def test_input_cache_isolation_between_accounts():
    # Arrange
    ctx = Context(year=2024, day=1, part=1)
    cookies1 = {"session": "account1_token"}
    cookies2 = {"session": "account2_token"}
    content1 = "Account 1 puzzle input"
    content2 = "Account 2 puzzle input"

    with tempfile.TemporaryDirectory() as tmpdir:
        with patch("pathlib.Path.home", return_value=Path(tmpdir)):
            # Act - Write cache for both accounts
            write_input_cache(ctx, cookies1, content1)
            write_input_cache(ctx, cookies2, content2)

            # Act - Read cache for both accounts
            cached1 = read_input_cache(ctx, cookies1)
            cached2 = read_input_cache(ctx, cookies2)

            # Assert - Each account gets its own cached content
            assert cached1 == content1
            assert cached2 == content2
            assert cached1 != cached2

@patch("requests.get")
def test_get_input_uses_cache(mock_get):
    # Arrange
    ctx = Context(year=2024, day=1, part=1)
    cached_data = "cached puzzle input"
    cookies = {"session": "test_token"}

    with patch("aoc.input.get_session_cookies", return_value=cookies):
        with patch("aoc.input.read_input_cache", return_value=cached_data):
            # Act
            result = get_input(ctx)

            # Assert - Should return cached data without making HTTP request
            assert result.raw == cached_data
            mock_get.assert_not_called()

@patch("requests.get")
def test_get_input_caches_on_fetch(mock_get):
    # Arrange
    ctx = Context(year=2024, day=2, part=1)
    fetched_data = "freshly fetched input"
    cookies = {"session": "mock_token"}
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.text = fetched_data
    mock_get.return_value = mock_response

    with tempfile.TemporaryDirectory() as tmpdir:
        with patch("pathlib.Path.home", return_value=Path(tmpdir)):
            with patch("aoc.input.get_session_cookies", return_value=cookies):
                # Act - First call should fetch and cache
                result = get_input(ctx)

                # Assert - Data is correct
                assert result.raw == fetched_data
                mock_get.assert_called_once()

                # Assert - Cache file was created
                cache_path = get_input_cache_path(ctx, cookies)
                assert cache_path.exists()
                assert cache_path.read_text() == fetched_data

@patch("requests.get")
def test_get_input_cache_avoids_second_request(mock_get):
    # Arrange
    ctx = Context(year=2024, day=3, part=1)
    fetched_data = "puzzle input from web"
    cookies = {"session": "mock_token"}
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.text = fetched_data
    mock_get.return_value = mock_response

    with tempfile.TemporaryDirectory() as tmpdir:
        with patch("pathlib.Path.home", return_value=Path(tmpdir)):
            with patch("aoc.input.get_session_cookies", return_value=cookies):
                # Act - First call
                result1 = get_input(ctx)
                assert result1.raw == fetched_data
                assert mock_get.call_count == 1

                # Act - Second call should use cache
                result2 = get_input(ctx)

                # Assert - No additional HTTP request
                assert mock_get.call_count == 1
                assert result2.raw == fetched_data

# endregion
