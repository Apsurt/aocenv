import re
from typing import (
    Any,
    Callable,
    Generic,
    TypeVar,
    List,
    Tuple,
    Dict,
    Iterable,
    Optional,
)
import requests
from .context import Context, get_context
from .configuration import get_session_cookies
from .cache import read_input_cache, write_input_cache

# Type variable for generic usage
T = TypeVar("T")


class Grid(Generic[T]):
    def __init__(self, data: List[List[T]]):
        self.data: List[List[T]] = data
        self.height: int = len(data)
        self.width: int = len(data[0]) if self.height > 0 else 0

    def get(self, r: int, c: int, default: Any = None) -> T | None:
        if 0 <= r < self.height and 0 <= c < self.width:
            return self.data[r][c]
        return default

    def neighbors(
        self, r: int, c: int, diagonals: bool = False
    ) -> Dict[Tuple[int, int], T]:
        neighbors_map = {}
        deltas = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        if diagonals:
            deltas.extend([(-1, -1), (-1, 1), (1, -1), (1, 1)])

        for dr, dc in deltas:
            nr, nc = r + dr, c + dc
            if 0 <= nr < self.height and 0 <= nc < self.width:
                neighbors_map[(nr, nc)] = self.data[nr][nc]
        return neighbors_map

    def transpose(self) -> "Grid[T]":
        transposed_data = [list(row) for row in zip(*self.data)]
        return Grid(transposed_data)

    def rows(self) -> Iterable[List[T]]:
        return iter(self.data)

    def cols(self) -> Iterable[Tuple[T, ...]]:
        return iter(zip(*self.data))

    def __repr__(self) -> str:
        return f"<Grid height={self.height} width={self.width}>"


def _recursive_apply(func: Callable, data: Any) -> Any:
    if isinstance(data, list):
        return [_recursive_apply(func, item) for item in data]
    try:
        # Attempt to apply the function, but return original on failure
        # This is useful for to_int/to_float on mixed-type data.
        return func(data)
    except (ValueError, TypeError):
        return data


class Input:
    raw: str
    _value: Any

    def __init__(self, raw_data: str | None = None):
        if raw_data is None:
            fetched_input = get_input(get_context())
            self.raw = fetched_input.raw
            self._value = fetched_input.raw
        else:
            self.raw = raw_data
            self._value = raw_data

    def __len__(self) -> int:
        if hasattr(self._value, "__len__"):
            return len(self._value)
        return 1

    def __iter__(self) -> Iterable:
        if hasattr(self._value, "__iter__") and not isinstance(self._value, str):
            return iter(self._value)
        return iter([self._value])

    def __getitem__(self, key: int | slice) -> Any:
        if isinstance(self._value, list):
            return self._value[key]
        raise TypeError(
            f"Current value of type '{type(self._value).__name__}' is not subscriptable."
        )

    # --- Chainable Methods (return self) ---
    def strip(self) -> "Input":
        if isinstance(self._value, str):
            self._value = self._value.strip()
        elif isinstance(self._value, list):
            self._value = [s.strip() for s in self._value if isinstance(s, str)]
        return self

    def lines(self) -> "Input":
        if isinstance(self._value, str):
            self._value = [line for line in self._value.strip().split("\n") if line]
        return self

    def paragraphs(self) -> "Input":
        if isinstance(self._value, str):
            self._value = [p.strip() for p in self._value.strip().split("\n\n") if p]
        return self

    def split(self, sep: Optional[str] = None) -> "Input":
        if isinstance(self._value, str):
            self._value = self._value.split(sep)
        elif isinstance(self._value, list):
            self._value = [item.split(sep) for item in self._value]
        return self

    def map(self, func: Callable) -> "Input":
        if isinstance(self._value, list):
            self._value = [func(item) for item in self._value]
        else:
            self._value = func(self._value)
        return self

    def filter(self, func: Callable) -> "Input":
        if isinstance(self._value, list):
            self._value = [item for item in self._value if func(item)]
        return self

    def flatten(self) -> "Input":
        if (
            isinstance(self._value, list)
            and self._value
            and isinstance(self._value[0], list)
        ):
            self._value = [item for sublist in self._value for item in sublist]
        return self

    def findall(self, pattern: str) -> "Input":
        if isinstance(self._value, str):
            self._value = re.findall(pattern, self._value)
        elif isinstance(self._value, list):
            self._value = [re.findall(pattern, item) for item in self._value]
        return self

    def to_int(self) -> "Input":
        self._value = _recursive_apply(int, self._value)
        return self

    def to_float(self) -> "Input":
        self._value = _recursive_apply(float, self._value)
        return self

    # --- Finalizers / Getters ---
    def get(self) -> Any:
        return self._value

    def grid(self) -> Grid:
        grid_data = []
        if isinstance(self._value, str):
            lines = self._value.strip().split("\n")
            grid_data = [list(line) for line in lines]
        elif (
            isinstance(self._value, list)
            and self._value
            and isinstance(self._value[0], str)
        ):
            grid_data = [list(line) for line in self._value]
        elif (
            isinstance(self._value, list)
            and self._value
            and isinstance(self._value[0], list)
        ):
            grid_data = self._value
        else:
            raise TypeError(
                f"Cannot convert type '{type(self._value).__name__}' to a Grid."
            )
        return Grid(grid_data)


def get_input(ctx: Context) -> "Input":
    cookies = get_session_cookies()
    if not cookies or "session" not in cookies:
        raise ValueError("Session cookie is not set.")

    # Check cache first
    cached_content = read_input_cache(ctx, cookies)
    if cached_content is not None:
        return Input(cached_content)

    # Fetch from web if not cached
    url = f"https://adventofcode.com/{ctx.year}/day/{ctx.day}/input"

    try:
        response = requests.get(url, cookies=cookies)
        response.raise_for_status()
        content = response.text

        # Cache the result
        write_input_cache(ctx, cookies, content)

        return Input(content)
    except requests.exceptions.RequestException as e:
        raise RuntimeError(f"Failed to fetch input: {e}") from e
