from pathlib import Path
from .context import Context
from typing import Optional


def get_solution_filename(ctx: Context, name: Optional[str]):
    filename = f"{ctx.year}_{ctx.day}_{ctx.part}"
    if name:
        filename += "_" + name
    filename += ".py"
    return filename


def get_solution_path(base_path: Path, ctx: Context):
    return base_path / "solutions" / str(ctx.year) / str(ctx.day)
