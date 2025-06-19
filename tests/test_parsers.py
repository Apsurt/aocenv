import pytest
import numpy as np
from aoc.parsers import InputParser


@pytest.fixture
def sample_input():
	"""Provides a multi-line, multi-block sample input for tests."""
	return """1
2
3

a,b,c
d,e,f

#.#
.#.
###
"""


def test_parser_lines(sample_input):
	"""Tests splitting the input into lines, ignoring blank lines."""
	parser = InputParser(sample_input)
	lines = parser.lines().get()
	# The new implementation filters the two blank lines.
	assert len(lines) == 8
	assert lines[0] == "1"
	assert lines[3] == "a,b,c"


def test_parser_blocks(sample_input):
	"""Tests splitting the input into blocks."""
	parser = InputParser(sample_input)
	blocks = parser.blocks().get()
	assert len(blocks) == 3
	assert blocks[0] == "1\n2\n3"
	assert blocks[2] == "#.#\n.#.\n###"


def test_parser_chaining_to_ints():
	"""Tests chaining methods to get a list of integers."""
	input_str = "1\n2\n3"
	parser = InputParser(input_str)
	numbers = parser.lines().to_ints().get()
	assert numbers == [1, 2, 3]


def test_parser_split_and_strip():
	"""Tests using split and strip methods."""
	input_str = " a , b , c "
	parser = InputParser(input_str)
	# Chain strip -> split -> strip again for each element
	items = parser.strip().split(on=",").strip().get()
	assert items == ["a", "b", "c"]


def test_parser_to_grid():
	"""Tests the to_grid terminator."""
	input_str = "#.#\n.#."
	parser = InputParser(input_str)
	grid = parser.to_grid()
	assert grid == [["#", ".", "#"], [".", "#", "."]]


def test_parser_composite_blocks_to_grids(sample_input):
	"""Tests the composite parsing of blocks into multiple grids."""
	parser = InputParser(sample_input)
	# This gets blocks, then applies to_grid to each block
	list_of_grids = parser.blocks().to_grid()
	assert len(list_of_grids) == 3
	assert list_of_grids[2] == [["#", ".", "#"], [".", "#", "."], ["#", "#", "#"]]


def test_parser_to_numpy():
	"""Tests converting a grid to a NumPy array."""
	input_str = "1 2\n3 4"
	parser = InputParser(input_str)
	# Use split to handle spaces, then convert to a numpy array of integers
	np_array = parser.lines().split(on=" ").to_numpy(dtype=int)
	assert isinstance(np_array, np.ndarray)
	assert np_array.shape == (2, 2)
	assert np_array[1, 1] == 4


def test_parser_regex_extract():
	"""Tests the regex .extract() method."""
	input_str = "pos=<1, 5, -2>, r=6"
	parser = InputParser(input_str)
	# Extract all numbers from the string
	extracted = parser.extract(r"(-?\d+)").to_ints().get()
	# The result for a single line of text is a flat list.
	assert extracted == [1, 5, -2, 6]


def test_parser_regex_with_multiple_lines():
	"""Tests applying regex extract to multiple lines."""
	input_str = "mem[8] = 11\nmem[7] = 101"
	parser = InputParser(input_str)
	data = parser.lines().extract(r"mem\[(\d+)\] = (\d+)").to_ints().get()
	# The new _apply_to_elements handles the tuples from findall correctly.
	assert data == [[(8, 11)], [(7, 101)]]
