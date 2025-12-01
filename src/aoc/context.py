import os
import ast
from dataclasses import dataclass
from pathlib import Path
from typing import Optional
from .configuration import get_config


@dataclass
class Context:
    year: int
    day: int
    part: int

    def __post_init__(self):
        if not (2015 <= self.year <= 2030):
            raise ValueError(f"Invalid year: {self.year}")
        if not (1 <= self.day <= 25):
            raise ValueError(f"Invalid day: {self.day}")
        if self.part not in (1, 2):
            raise ValueError(f"Invalid part: {self.part}")


def find_project_root(start_path: Optional[str] = None) -> Optional[Path]:
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
    constants: dict[str, int | None] = {"year": None, "day": None, "part": None}

    try:
        with open(main_path, "r") as f:
            tree = ast.parse(f.read(), filename=str(main_path))

        # Walk through the AST to find assignments
        for node in ast.walk(tree):
            if isinstance(node, ast.Assign):
                # Handle simple assignments like: YEAR = 2024
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        if target.id == "YEAR" and isinstance(node.value, ast.Constant):
                            if isinstance(node.value.value, int):
                                constants["year"] = node.value.value
                        elif target.id == "DAY" and isinstance(
                            node.value, ast.Constant
                        ):
                            if isinstance(node.value.value, int):
                                constants["day"] = node.value.value
                        elif target.id == "PART" and isinstance(
                            node.value, ast.Constant
                        ):
                            if isinstance(node.value.value, int):
                                constants["part"] = node.value.value

                    # Handle tuple unpacking like: YEAR, DAY, PART = (2024, 15, 1)
                    elif isinstance(target, ast.Tuple):
                        if isinstance(node.value, (ast.Tuple, ast.List)):
                            names = [
                                t.id for t in target.elts if isinstance(t, ast.Name)
                            ]
                            values = [
                                v.value
                                for v in node.value.elts
                                if isinstance(v, ast.Constant)
                            ]

                            for name, value in zip(names, values):
                                if isinstance(value, int):
                                    if name == "YEAR":
                                        constants["year"] = value
                                    elif name == "DAY":
                                        constants["day"] = value
                                    elif name == "PART":
                                        constants["part"] = value

    except (OSError, SyntaxError):
        pass

    return constants


def get_context() -> Context:
    # Find project root
    project_root = find_project_root()

    if project_root is None:
        # Fallback to defaults if project root not found
        return Context(2025, 1, 1)

    # Extract constants from main.py
    main_path = project_root / "main.py"
    constants = extract_constants_from_main(main_path)

    config = get_config()
    # Use extracted values or fall back to defaults
    year = (
        constants["year"]
        if constants["year"] is not None
        else config.getint("variables", "default_year")
    )
    day = (
        constants["day"]
        if constants["day"] is not None
        else config.getint("variables", "default_day")
    )
    part = (
        constants["part"]
        if constants["part"] is not None
        else config.getint("variables", "default_part")
    )

    return Context(year, day, part)
