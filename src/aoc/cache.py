"""
Cache management for Advent of Code puzzle inputs and submissions.
"""
from enum import Enum
import hashlib
from pathlib import Path
from typing import Dict
from .context import Context


def _get_session_hash(cookies: Dict[str, str]) -> str:
    """
    Creates a hash of the session cookie to differentiate between accounts.

    Args:
        cookies: Dictionary containing session cookies.

    Returns:
        First 8 characters of the SHA256 hash of the session cookie.
    """
    session = cookies.get("session", "")
    return hashlib.sha256(session.encode()).hexdigest()[:8]


def get_input_cache_path(ctx: Context, cookies: Dict[str, str]) -> Path:
    """
    Returns the cache file path for puzzle input for a given year, day, and session.

    Args:
        ctx: The context object containing the year and day.
        cookies: Dictionary containing session cookies.

    Returns:
        Path to the input cache file.
    """
    session_hash = _get_session_hash(cookies)
    cache_dir = Path(".aoc") / "cache" / session_hash / str(ctx.year) / "inputs"
    return cache_dir / f"day{ctx.day}.txt"


def read_input_cache(ctx: Context, cookies: Dict[str, str]) -> str | None:
    """
    Reads cached puzzle input if available.

    Args:
        ctx: The context object containing the year and day.
        cookies: Dictionary containing session cookies.

    Returns:
        Cached puzzle input or None if not cached.
    """
    cache_path = get_input_cache_path(ctx, cookies)
    if cache_path.exists():
        return cache_path.read_text()
    return None


def write_input_cache(ctx: Context, cookies: Dict[str, str], content: str) -> None:
    """
    Writes puzzle input to cache.

    Args:
        ctx: The context object containing the year and day.
        cookies: Dictionary containing session cookies.
        content: The puzzle input to cache.
    """
    cache_path = get_input_cache_path(ctx, cookies)
    cache_path.parent.mkdir(parents=True, exist_ok=True)
    cache_path.write_text(content)

class Results(Enum):
    WRONG = 0
    CORRECT = 1
    TOO_FAST = 2
    ANSWERED = 3

def get_submit_cache_path(ctx: Context, cookies: Dict[str, str]) -> Path:
    session_hash = _get_session_hash(cookies)
    cache_dir = Path(".aoc") / "cache" / session_hash / str(ctx.year) / "submits"
    return cache_dir / f"day{ctx.day}part{ctx.part}.json"

def read_submit_cache():
    pass

def write_submit_cache() -> None:
    pass
