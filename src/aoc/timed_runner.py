# src/aoc/timed_runner.py
import time
import importlib.util
import sys
import os
import ast
from aoc.timing_context import get_total_submit_time

MAIN_SCRIPT = "main.py"

def main_function_exists(filepath):
    """Safely checks for a main function using AST without executing the file."""
    if not os.path.exists(filepath):
        return False
    with open(filepath, "r", encoding="utf-8") as f:
        tree = ast.parse(f.read(), filename=filepath)
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "main":
            return True
    return False


def run_script_unstimed():
    """Runs the script normally using runpy if timing can't be done."""
    import runpy
    runpy.run_path(MAIN_SCRIPT, run_name="__main__")


# 1. Check for main function before doing anything else.
if not main_function_exists(MAIN_SCRIPT):
    print(
        f"Warning: '{MAIN_SCRIPT}' does not contain a 'main' function. Running script without timing.",
        file=sys.stderr,
    )
    run_script_unstimed()
    sys.exit(0)


# 2. If main exists, import the script as a module. This will run top-level code.
try:
    spec = importlib.util.spec_from_file_location("main", MAIN_SCRIPT)
    if spec is None or spec.loader is None:
        raise ImportError(f"Could not create module spec for {MAIN_SCRIPT}.")
    user_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(user_module)
except Exception as e:
    print(f"Error during import of {MAIN_SCRIPT}: {e}", file=sys.stderr)
    import traceback
    traceback.print_exc(file=sys.stderr)
    sys.exit(1)


# 3. Get a reference to the main function and time its execution.
main_func = getattr(user_module, "main")
final_time = -1.0
total_duration = -1.0
submit_duration = -1.0

try:
    start_time = time.perf_counter()
    main_func()
    end_time = time.perf_counter()

    total_duration = end_time - start_time
    submit_duration = get_total_submit_time()
    final_time = total_duration - submit_duration

except Exception as e:
    print(f"Error during execution of main(): {e}", file=sys.stderr)
    import traceback
    traceback.print_exc(file=sys.stderr)
finally:
    # 4. Report the results.
    print("\n" + "=" * 40, file=sys.stderr)
    if final_time >= 0:
        print(f"  Execution time : {final_time:.6f} seconds", file=sys.stderr)
    print("=" * 40, file=sys.stderr)
