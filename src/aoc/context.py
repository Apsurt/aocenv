import os
import ast
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

@dataclass
class Context:
    year: int
    day: int
    part: int


def find_project_root(start_path: Optional[str] = None) -> Optional[Path]:
    """
    Searches upward from start_path to find the project root directory.
    The project root is identified by the presence of both main.py and config.toml.

    Args:
        start_path: Starting directory for the search. Defaults to current working directory.

    Returns:
        Path to the project root, or None if not found.
    """
    if start_path is None:
        start_path = os.getcwd()

    current = Path(start_path).resolve()

    # Search upward through parent directories
    while True:
        if (current / "main.py").exists() and (current / "config.toml").exists():
            return current

        # Check if we've reached the filesystem root
        parent = current.parent
        if parent == current:
            return None

        current = parent


def extract_constants_from_main(main_path: Path) -> dict[str, int | None]:
    """
    Uses AST to extract YEAR, DAY, and PART constants from main.py.

    Args:
        main_path: Path to the main.py file.

    Returns:
        Dictionary with keys 'year', 'day', 'part' (values are None if not found).
    """
    constants: dict[str, int | None] = {'year': None, 'day': None, 'part': None}

    try:
        with open(main_path, 'r') as f:
            tree = ast.parse(f.read(), filename=str(main_path))

        # Walk through the AST to find assignments
        for node in ast.walk(tree):
            if isinstance(node, ast.Assign):
                # Handle simple assignments like: YEAR = 2024
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        if target.id == 'YEAR' and isinstance(node.value, ast.Constant):
                            if isinstance(node.value.value, int):
                                constants['year'] = node.value.value
                        elif target.id == 'DAY' and isinstance(node.value, ast.Constant):
                            if isinstance(node.value.value, int):
                                constants['day'] = node.value.value
                        elif target.id == 'PART' and isinstance(node.value, ast.Constant):
                            if isinstance(node.value.value, int):
                                constants['part'] = node.value.value

                    # Handle tuple unpacking like: YEAR, DAY, PART = (2024, 15, 1)
                    elif isinstance(target, ast.Tuple):
                        if isinstance(node.value, (ast.Tuple, ast.List)):
                            names = [t.id for t in target.elts if isinstance(t, ast.Name)]
                            values = [v.value for v in node.value.elts if isinstance(v, ast.Constant)]

                            for name, value in zip(names, values):
                                if isinstance(value, int):
                                    if name == 'YEAR':
                                        constants['year'] = value
                                    elif name == 'DAY':
                                        constants['day'] = value
                                    elif name == 'PART':
                                        constants['part'] = value

    except (OSError, SyntaxError):
        pass

    return constants


def get_context() -> Context:
    """
    Retrieves the context (year, day, part) by parsing the main.py file.
    Falls back to default values if constants cannot be found.

    Returns:
        Context object with year, day, and part.
    """
    # Find project root
    project_root = find_project_root()

    if project_root is None:
        # Fallback to defaults if project root not found
        return Context(2024, 1, 1)

    # Extract constants from main.py
    main_path = project_root / "main.py"
    constants = extract_constants_from_main(main_path)

    # Use extracted values or fall back to defaults
    year = constants['year'] if constants['year'] is not None else 2024
    day = constants['day'] if constants['day'] is not None else 1
    part = constants['part'] if constants['part'] is not None else 1

    return Context(year, day, part)
