import os
from typing import Optional
from pathlib import Path
from .misc import get_solution_filename, get_solution_path
from .configuration import get_config
from .context import Context

def run_load(ctx: Context, name: Optional[str]):
    config = get_config()
    base_path = Path(config["variables"]["path"])

    filename = get_solution_filename(ctx, name)
    main_path = base_path / "main.py"
    solution_path = get_solution_path(base_path, ctx) / filename

    if not os.path.exists(solution_path):
        raise FileNotFoundError(f"There is no binded solution: {solution_path}")

    with open(solution_path, "r") as source:
        contents = source.read()

    # TODO check if main is empty

    with open(main_path, "w") as dest:
        dest.write(contents)
