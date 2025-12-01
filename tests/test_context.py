"""Tests for context resolution functionality."""

import tempfile
import os
from pathlib import Path
import configparser
from aoc.context import (
    Context,
    find_project_root,
    extract_constants_from_main,
    get_context,
)


def test_context_dataclass():
    """Test that Context dataclass works correctly."""
    ctx = Context(year=2024, day=15, part=2)
    assert ctx.year == 2024
    assert ctx.day == 15
    assert ctx.part == 2


def test_find_project_root_not_found():
    """Test that find_project_root returns None when no project found."""
    with tempfile.TemporaryDirectory() as tmpdir:
        result = find_project_root(tmpdir)
        assert result is None


def test_find_project_root_found():
    """Test that find_project_root finds the project root."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create main.py and config.toml
        Path(tmpdir, "main.py").touch()
        Path(tmpdir, "config.toml").touch()

        result = find_project_root(tmpdir)
        assert result == Path(tmpdir)


def test_find_project_root_nested():
    """Test that find_project_root searches upward from nested directories."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create main.py and config.toml in root
        Path(tmpdir, "main.py").touch()
        Path(tmpdir, "config.toml").touch()

        # Create nested directory
        nested_dir = Path(tmpdir, "subdir", "nested")
        nested_dir.mkdir(parents=True)

        result = find_project_root(str(nested_dir))
        assert result == Path(tmpdir)


def test_extract_constants_simple_assignment():
    """Test extracting constants from simple assignments."""
    with tempfile.TemporaryDirectory() as tmpdir:
        main_path = Path(tmpdir, "main.py")
        main_path.write_text("""
YEAR = 2024
DAY = 15
PART = 2
""")

        constants = extract_constants_from_main(main_path)
        assert constants == {"year": 2024, "day": 15, "part": 2}


def test_extract_constants_tuple_unpacking():
    """Test extracting constants from tuple unpacking."""
    with tempfile.TemporaryDirectory() as tmpdir:
        main_path = Path(tmpdir, "main.py")
        main_path.write_text("""
YEAR, DAY, PART = 2023, 10, 1
""")

        constants = extract_constants_from_main(main_path)
        assert constants == {"year": 2023, "day": 10, "part": 1}


def test_extract_constants_tuple_with_parens():
    """Test extracting constants from tuple with parentheses."""
    with tempfile.TemporaryDirectory() as tmpdir:
        main_path = Path(tmpdir, "main.py")
        main_path.write_text("""
YEAR, DAY, PART = (2022, 25, 2)
""")

        constants = extract_constants_from_main(main_path)
        assert constants == {"year": 2022, "day": 25, "part": 2}


def test_extract_constants_list_unpacking():
    """Test extracting constants from list unpacking."""
    with tempfile.TemporaryDirectory() as tmpdir:
        main_path = Path(tmpdir, "main.py")
        main_path.write_text("""
YEAR, DAY, PART = [2021, 12, 1]
""")

        constants = extract_constants_from_main(main_path)
        assert constants == {"year": 2021, "day": 12, "part": 1}


def test_extract_constants_partial():
    """Test extracting constants when only some are present."""
    with tempfile.TemporaryDirectory() as tmpdir:
        main_path = Path(tmpdir, "main.py")
        main_path.write_text("""
YEAR = 2024
DAY = 5
""")

        constants = extract_constants_from_main(main_path)
        assert constants == {"year": 2024, "day": 5, "part": None}


def test_extract_constants_missing_file():
    """Test extracting constants when file doesn't exist."""
    constants = extract_constants_from_main(Path("/nonexistent/main.py"))
    assert constants == {"year": None, "day": None, "part": None}


def test_extract_constants_invalid_syntax():
    """Test extracting constants with invalid Python syntax."""
    with tempfile.TemporaryDirectory() as tmpdir:
        main_path = Path(tmpdir, "main.py")
        main_path.write_text("YEAR = 2024\nthis is not valid python")

        constants = extract_constants_from_main(main_path)
        assert constants == {"year": None, "day": None, "part": None}


def test_get_context_with_project():
    """Test get_context when in a valid project directory."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create main.py with constants
        main_path = Path(tmpdir, "main.py")
        main_path.write_text("""
YEAR = 2024
DAY = 15
PART = 2

def solve():
    pass
""")
        # Create config.toml
        config = configparser.ConfigParser()
        config["variables"] = {
            "default_year": "2025",
            "default_day": "1",
            "default_part": "1",
        }
        with open(Path(tmpdir, "config.toml"), "w") as f:
            config.write(f)

        # Change to the temp directory
        old_cwd = os.getcwd()
        try:
            os.chdir(tmpdir)
            ctx = get_context()
            assert ctx.year == 2024
            assert ctx.day == 15
            assert ctx.part == 2
        finally:
            os.chdir(old_cwd)


def test_get_context_fallback():
    """Test get_context falls back to defaults when no project found."""
    with tempfile.TemporaryDirectory() as tmpdir:
        old_cwd = os.getcwd()
        try:
            os.chdir(tmpdir)
            ctx = get_context()
            assert ctx.year == 2025
            assert ctx.day == 1
            assert ctx.part == 1
        finally:
            os.chdir(old_cwd)

def test_get_context_partial_constants():
    """Test get_context with partial constants uses defaults for missing values."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create main.py with only YEAR and DAY
        main_path = Path(tmpdir, "main.py")
        main_path.write_text("""
YEAR = 2023
DAY = 10
""")
        # Create config.toml with different defaults
        config = configparser.ConfigParser()
        config["variables"] = {
            "default_year": "2000",
            "default_day": "20",
            "default_part": "2",
        }
        with open(Path(tmpdir, "config.toml"), "w") as f:
            config.write(f)

        old_cwd = os.getcwd()
        try:
            os.chdir(tmpdir)
            ctx = get_context()
            assert ctx.year == 2023  # From main.py
            assert ctx.day == 10  # From main.py
            assert ctx.part == 2  # Fallback to config
        finally:
            os.chdir(old_cwd)


def test_get_context_fallback_to_config():
    """Test get_context falls back to config when no context in main.py."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create main.py with no context
        main_path = Path(tmpdir, "main.py")
        main_path.write_text("def solve(): pass")

        # Create config.toml with custom defaults
        config = configparser.ConfigParser()
        config["variables"] = {
            "default_year": "2021",
            "default_day": "22",
            "default_part": "1",
        }
        with open(Path(tmpdir, "config.toml"), "w") as f:
            config.write(f)

        old_cwd = os.getcwd()
        try:
            os.chdir(tmpdir)
            ctx = get_context()
            assert ctx.year == 2021
            assert ctx.day == 22
            assert ctx.part == 1
        finally:
            os.chdir(old_cwd)
