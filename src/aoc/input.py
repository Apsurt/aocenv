"""
Provides a powerful, fluent interface for parsing Advent of Code puzzle inputs.
"""
import re
from typing import Any, Callable, Generic, TypeVar, List, Tuple, Dict, Iterable

# Type variable for generic usage
T = TypeVar('T')


class Grid(Generic[T]):
    """
    A helper class for working with 2D grid data. It is typically instantiated
    via the `Input.grid()` method.
    """
    def __init__(self, data: List[List[T]]):
        self.data: List[List[T]] = data
        self.height: int = len(data)
        self.width: int = len(data[0]) if self.height > 0 else 0

    def get(self, r: int, c: int, default: Any = None) -> T | None:
        """Safely gets the value at a given coordinate (row, col)."""
        if 0 <= r < self.height and 0 <= c < self.width:
            return self.data[r][c]
        return default

    def neighbors(self, r: int, c: int, diagonals: bool = False) -> Dict[Tuple[int, int], T]:
        """
        Gets all neighboring cells for a given coordinate.

        Args:
            r: The row of the cell.
            c: The column of the cell.
            diagonals: If True, includes diagonal neighbors.

        Returns:
            A dictionary mapping neighbor coordinates to their values.
        """
        neighbors_map = {}
        deltas = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        if diagonals:
            deltas.extend([(-1, -1), (-1, 1), (1, -1), (1, 1)])

        for dr, dc in deltas:
            nr, nc = r + dr, c + dc
            if 0 <= nr < self.height and 0 <= nc < self.width:
                neighbors_map[(nr, nc)] = self.data[nr][nc]
        return neighbors_map

    def transpose(self) -> 'Grid[T]':
        """Returns a new Grid with rows and columns swapped."""
        transposed_data = [list(row) for row in zip(*self.data)]
        return Grid(transposed_data)

    def rows(self) -> Iterable[List[T]]:
        """Returns an iterator over the rows of the grid."""
        return iter(self.data)

    def cols(self) -> Iterable[Tuple[T, ...]]:
        """Returns an iterator over the columns of the grid."""
        return iter(zip(*self.data))

    def __repr__(self) -> str:
        return f"<Grid height={self.height} width={self.width}>"


def _recursive_apply(func: Callable, data: Any) -> Any:
    """Helper to recursively apply a function to nested lists."""
    if isinstance(data, list):
        return [_recursive_apply(func, item) for item in data]
    try:
        # Attempt to apply the function, but return original on failure
        # This is useful for to_int/to_float on mixed-type data.
        return func(data)
    except (ValueError, TypeError):
        return data


class Input:
    """
    A fluent interface for parsing raw string inputs, inspired by common
    Advent of Code data structures.
    """
    def __init__(self, raw_data: str):
        self.raw: str = raw_data
        self._value: Any = raw_data

    # --- Pythonic Integration ---
    def __len__(self) -> int:
        if hasattr(self._value, '__len__'):
            return len(self._value)
        return 1

    def __iter__(self) -> Iterable:
        if hasattr(self._value, '__iter__') and not isinstance(self._value, str):
            return iter(self._value)
        return iter([self._value])

    def __getitem__(self, key: int | slice) -> Any:
        if isinstance(self._value, list):
            return self._value[key]
        raise TypeError(f"Current value of type '{type(self._value).__name__}' is not subscriptable.")

    # --- Chainable Methods (return self) ---
    def strip(self) -> 'Input':
        """Strips whitespace from string or list of strings."""
        if isinstance(self._value, str):
            self._value = self._value.strip()
        elif isinstance(self._value, list):
            self._value = [s.strip() for s in self._value if isinstance(s, str)]
        return self

    def lines(self) -> 'Input':
        """Splits the input into a list of non-empty lines."""
        if isinstance(self._value, str):
            self._value = [line for line in self._value.strip().split('\n') if line]
        return self

    def paragraphs(self) -> 'Input':
        """Splits the input by blank lines into a list of paragraph strings."""
        if isinstance(self._value, str):
            self._value = [p.strip() for p in self._value.strip().split('\n\n') if p]
        return self

    def split(self, sep: str) -> 'Input':
        """Splits a string or each string in a list by a separator."""
        if isinstance(self._value, str):
            self._value = self._value.split(sep)
        elif isinstance(self._value, list):
            self._value = [item.split(sep) for item in self._value]
        return self

    def map(self, func: Callable) -> 'Input':
        """Applies a function to the value or each item in a list."""
        if isinstance(self._value, list):
            self._value = [func(item) for item in self._value]
        else:
            self._value = func(self._value)
        return self

    def filter(self, func: Callable) -> 'Input':
        """Filters a list based on a predicate function."""
        if isinstance(self._value, list):
            self._value = [item for item in self._value if func(item)]
        return self

    def flatten(self) -> 'Input':
        """Flattens a list of lists into a single list."""
        if isinstance(self._value, list) and self._value and isinstance(self._value[0], list):
            self._value = [item for sublist in self._value for item in sublist]
        return self

    def findall(self, pattern: str) -> 'Input':
        """For each string, finds all occurrences of a regex pattern."""
        if isinstance(self._value, str):
            self._value = re.findall(pattern, self._value)
        elif isinstance(self._value, list):
            self._value = [re.findall(pattern, item) for item in self._value]
        return self

    def to_int(self) -> 'Input':
        """Recursively converts values to integers."""
        self._value = _recursive_apply(int, self._value)
        return self

    def to_float(self) -> 'Input':
        """Recursively converts values to floats."""
        self._value = _recursive_apply(float, self._value)
        return self

    # --- Finalizers / Getters ---
    def get(self) -> Any:
        """Returns the final parsed value."""
        return self._value

    def grid(self) -> Grid:
        """
        Converts the current value to a Grid object.
        The value should be a list of strings, a list of lists, or a
        string that can be split into lines.
        """
        grid_data = []
        if isinstance(self._value, str):
            lines = self._value.strip().split('\n')
            grid_data = [list(line) for line in lines]
        elif isinstance(self._value, list) and self._value and isinstance(self._value[0], str):
            grid_data = [list(line) for line in self._value]
        elif isinstance(self._value, list) and self._value and isinstance(self._value[0], list):
            grid_data = self._value
        else:
            raise TypeError(f"Cannot convert type '{type(self._value).__name__}' to a Grid.")
        return Grid(grid_data)
