# src/aoc/bench.py
import os
import time
import importlib.util
import sys
from typing import Optional, Dict, List, Tuple
from pathlib import Path
import ast
from tqdm import tqdm
from rich.table import Table
from rich.console import Console

from .configuration import get_config
from .misc import get_solution_path, get_solution_filename
from .context import Context

def main_function_exists(filepath):
    """Safely checks for a main function using AST without executing the file."""
    if not os.path.exists(filepath):
        return False
    with open(filepath, "r", encoding="utf-8") as f:
        try:
            tree = ast.parse(f.read(), filename=filepath)
        except SyntaxError:
            return False
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "main":
            return True
    return False

def time_solution(script_path: Path) -> Optional[float]:
    """Times the execution of a single solution script."""
    if not script_path or not main_function_exists(script_path):
        return None

    try:
        # Dynamically import the script
        spec = importlib.util.spec_from_file_location("solution", script_path)
        if spec is None or spec.loader is None:
            return -1.0  # Indicate import failure
        module = importlib.util.module_from_spec(spec)

        # Suppress output
        original_stdout = sys.stdout
        original_stderr = sys.stderr
        sys.stdout = open(os.devnull, 'w')
        sys.stderr = open(os.devnull, 'w')

        try:
            spec.loader.exec_module(module)
            main_func = getattr(module, "main")

            start_time = time.perf_counter()
            main_func()
            end_time = time.perf_counter()

            return end_time - start_time
        finally:
            # Restore output streams
            sys.stdout.close()
            sys.stderr.close()
            sys.stdout = original_stdout
            sys.stderr = original_stderr

    except Exception:
        return -1.0 # Indicate execution failure

def find_solution_for_part(year: int, day: int, part: int, solutions_path: Path) -> Optional[Path]:
    """Finds the appropriate solution file for a given part."""
    day_path = solutions_path / str(year) / str(day)
    if not day_path.exists():
        return None

    # Try default filename first
    ctx = Context(year=year, day=day, part=part)
    default_filename = get_solution_filename(ctx, None)
    default_path = day_path / default_filename
    if default_path.exists():
        return default_path

    # If no default, find named alternatives and pick the first alphabetically
    glob_pattern = f"{year}_{day:02d}_{part}_*.py" # Assuming day is formatted with zero padding if needed

    # Let's re-check get_solution_filename to be sure about the format.
    # It seems it does not zero-pad. So let's adjust.
    glob_pattern = f"{year}_{day}_{part}_*.py"

    named_solutions = sorted(list(day_path.glob(glob_pattern)))
    if named_solutions:
        return named_solutions[0]

    return None

def run_benchmark(year: Optional[int]):
    config = get_config()
    solutions_root = Path(config["variables"]["path"]) / "solutions"

    years_to_scan = []
    if year:
        years_to_scan.append(year)
    else:
        if solutions_root.exists():
            years_to_scan = sorted([int(p.name) for p in solutions_root.iterdir() if p.is_dir() and p.name.isdigit()])

    results = []
    total_days = sum(1 for y in years_to_scan for d in range(1, 26))

    with tqdm(total=total_days, desc="Benchmarking") as pbar:
        for y in years_to_scan:
            for d in range(1, 26):
                pbar.set_description(f"Benchmarking: [{y} Day {d}]")
                pbar.update(1)

                part1_script = find_solution_for_part(y, d, 1, solutions_root)
                part2_script = find_solution_for_part(y, d, 2, solutions_root)

                if not part1_script and not part2_script:
                    continue

                part1_time = time_solution(part1_script) if part1_script else None
                part2_time = time_solution(part2_script) if part2_script else None

                day_total = (part1_time or 0.0) + (part2_time or 0.0)
                if day_total > 0:
                     results.append((y, d, part1_time, part2_time, day_total))

    # Display results
    console = Console()
    table = Table(title="AoC Benchmark Results")
    table.add_column("Year", justify="right")
    table.add_column("Day", justify="right")
    table.add_column("Part 1 Time", justify="right")
    table.add_column("Part 2 Time", justify="right")
    table.add_column("Day Total", justify="right")

    grand_total = 0.0
    for res in results:
        y, d, p1t, p2t, dt = res
        grand_total += dt

        p1s = f"{p1t:.6f}s" if p1t is not None and p1t >= 0 else ("SKIPPED" if p1t is None else "FAILED")
        p2s = f"{p2t:.6f}s" if p2t is not None and p2t >= 0 else ("SKIPPED" if p2t is None else "FAILED")
        dts = f"{dt:.6f}s" if dt >= 0 else "FAILED"

        table.add_row(str(y), str(d), p1s, p2s, dts)

    console.print(table)
    console.print(f"[bold]Grand Total: {grand_total:.6f}s[/bold]")
