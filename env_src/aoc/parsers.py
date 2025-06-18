import re
import numpy as np
from typing import Any, Callable, List

class InputParser:
    """A fluent interface for parsing Advent of Code puzzle inputs."""

    def __init__(self, data: str):
        """Initializes the parser with the raw string data."""
        self._data: Any = data

    def __iter__(self):
        """Allows iterating over the parsed data."""
        if isinstance(self._data, list):
            return iter(self._data)
        return iter([self._data])

    def _apply_to_elements(self, func: Callable, current_data: Any) -> Any:
        """Helper to apply a function to elements, handling nested lists."""
        if isinstance(current_data, list):
            return [self._apply_to_elements(func, item) for item in current_data]
        return func(current_data)

    # --- Transformer Methods (Chainable) ---

    def lines(self):
        """Splits the data into a list of strings by newlines."""
        if isinstance(self._data, str):
            self._data = self._data.strip().splitlines()
        return self

    def blocks(self):
        """Splits the data into blocks separated by blank lines."""
        if isinstance(self._data, str):
            self._data = self._data.strip().split('\n\n')
        return self

    def split(self, on: str):
        """Splits each string element by a given separator."""
        self._data = self._apply_to_elements(lambda s: s.split(on), self._data)
        return self

    def to_ints(self):
        """Converts each string element to an integer."""
        self._data = self._apply_to_elements(int, self._data)
        return self

    def strip(self):
        """Strips whitespace from each string element."""
        self._data = self._apply_to_elements(lambda s: s.strip(), self._data)
        return self

    def extract(self, pattern: str):
        """
        For each string, extracts all capture groups from a regex pattern.
        If the pattern has only one capture group, it returns a single value.
        If it has multiple, it returns a tuple of values.
        """
        compiled_pattern = re.compile(pattern)
        def _extractor(s: str) -> List[Any]:
            matches = compiled_pattern.findall(s)
            # If findall returns a list of tuples (multiple capture groups), it's already structured.
            # If it's a list of strings (one capture group), return as is.
            return matches
        self._data = self._apply_to_elements(_extractor, self._data)
        return self

    def findall(self, pattern: str):
        """For each string, finds all non-overlapping matches of a pattern."""
        self._data = self._apply_to_elements(lambda s: re.findall(pattern, s), self._data)
        return self

    def apply(self, func: Callable):
        """Applies a custom function to each element."""
        self._data = self._apply_to_elements(func, self._data)
        return self

    # --- Terminator Methods (Return Final Data) ---

    def get(self) -> Any:
        """Returns the final processed data."""
        return self._data

    def to_grid(self, delimiter: str = ''):
        """
        Parses string data into a 2D grid.
        - If the data is a single string, it becomes one grid.
        - If the data is a list of strings (blocks), it becomes a list of grids.
        """
        def _grid_parser(block: str) -> List[List[str]]:
            lines = block.strip().splitlines()
            if delimiter == '':
                return [list(line) for line in lines]
            else:
                return [line.split(delimiter) for line in lines]

        return self._apply_to_elements(_grid_parser, self._data)

    def to_numpy(self, dtype: Any = None):
        """
        Parses the data into a grid and returns it as a NumPy array.
        """
        # First, convert to a standard grid format
        grid_data = self.to_grid()

        # Now convert to numpy array
        if isinstance(grid_data[0][0], list): # This means we have a list of grids
             return [np.array(g, dtype=dtype) for g in grid_data]
        else: # A single grid
             return np.array(grid_data, dtype=dtype)
