import pytest

from aoc import tools


def test_manhattan_distance():
	"""Tests the manhattan_distance function."""
	assert tools.manhattan_distance((0, 0), (3, 4)) == 7
	assert tools.manhattan_distance((-1, -1), (1, 1)) == 4
	assert tools.manhattan_distance((10, 20), (10, 20)) == 0


def test_grid_class():
	"""Tests the Grid helper class."""
	grid_data = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
	grid = tools.Grid(grid_data)

	assert grid.width == 3
	assert grid.height == 3
	assert grid[1, 1] == 5

	# Test neighbors
	neighbors_center = set(grid.neighbors(1, 1))
	assert neighbors_center == {(0, 1), (2, 1), (1, 0), (1, 2)}

	neighbors_corner = set(grid.neighbors(0, 0, diagonal=True))
	assert neighbors_corner == {(1, 0), (0, 1), (1, 1)}


def test_merge_intervals():
	"""Tests the merge_intervals function."""
	intervals = [[1, 3], [2, 6], [8, 10], [15, 18]]
	assert tools.merge_intervals(intervals) == [[1, 6], [8, 10], [15, 18]]

	intervals_single = [[1, 5]]
	assert tools.merge_intervals(intervals_single) == [[1, 5]]

	intervals_no_overlap = [[1, 2], [3, 4]]
	assert tools.merge_intervals(intervals_no_overlap) == [[1, 2], [3, 4]]


def test_shoelace_area():
	"""Tests the shoelace_area function for a simple square."""
	vertices = [(0, 0), (4, 0), (4, 4), (0, 4)]
	assert tools.shoelace_area(vertices) == 16.0


def test_bfs_and_dfs():
	"""Tests the graph traversal algorithms."""
	graph = {"A": ["B", "C"], "B": ["D", "E"], "C": ["F"], "E": ["F"]}

	# BFS should visit level by level
	bfs_path = list(tools.bfs(graph, "A"))
	assert bfs_path == ["A", "B", "C", "D", "E", "F"]

	# DFS should go deep first
	dfs_path = list(tools.dfs(graph, "A"))
	assert dfs_path == ["A", "B", "D", "E", "F", "C"]


@pytest.fixture
def sample_recursive_func():
	"""Provides a sample Fibonacci-like function to test memoization."""

	@tools.memoize
	def fib(n):
		if n < 2:
			return n
		return fib(n - 1) + fib(n - 2)

	return fib


def test_memoize(sample_recursive_func):
	"""Tests the @memoize decorator."""
	assert sample_recursive_func(10) == 55
	# The real test is that this is fast. Pytest won't measure speed,
	# but correctness implies the cache is working.
	assert sample_recursive_func(35) == 9227465


def test_dijkstra():
	"""Tests the Dijkstra shortest path algorithm."""
	graph = {
		"A": [("B", 1), ("C", 4)],
		"B": [("A", 1), ("C", 2), ("D", 5)],
		"C": [("A", 4), ("B", 2), ("D", 1)],
		"D": [("B", 5), ("C", 1)],
	}
	distance, path = tools.dijkstra(graph, "A", "D")
	assert distance == 4
	assert path == ["A", "B", "C", "D"]
