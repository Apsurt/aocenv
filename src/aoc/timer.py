# src/aoc/timer.py
import time
import runpy
import os
import sys
import importlib.util

MAIN_SCRIPT = "main.py"

if not os.path.exists(MAIN_SCRIPT):
    print(f"Error: {MAIN_SCRIPT} not found.", file=sys.stderr)
    sys.exit(1)

# Get function name from command-line argument, if provided
func_to_time = sys.argv[1] if len(sys.argv) > 1 else None

# Announce what we're doing to stderr
print("-" * 40, file=sys.stderr)
if func_to_time:
    print(f"Attempting to time function: {func_to_time}()", file=sys.stderr)
else:
    print("Timing entire script execution.", file=sys.stderr)
print("-" * 40, file=sys.stderr)


start_time = time.perf_counter()
success = True
try:
    if func_to_time:
        # Import main.py as a module to access its functions
        spec = importlib.util.spec_from_file_location("main", MAIN_SCRIPT)
        if spec is None or spec.loader is None:
            raise ImportError(f"Could not create module spec for {MAIN_SCRIPT}.")
        user_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(user_module)

        # Get and run the specified function
        if hasattr(user_module, func_to_time):
            target_func = getattr(user_module, func_to_time)
            # Assuming the function takes no arguments.
            target_func()
        else:
            print(f"\nError: Function '{func_to_time}' not found in {MAIN_SCRIPT}.", file=sys.stderr)
            success = False
    else:
        # Time the whole script using runpy
        runpy.run_path(MAIN_SCRIPT, run_name="__main__")

except SystemExit:
    # Allow the user's script to call sys.exit() without stopping the timer report.
    pass
except Exception:
    # Catch other exceptions to ensure timer still reports, then print traceback
    print("\nAn error occurred during execution:", file=sys.stderr)
    import traceback
    traceback.print_exc(file=sys.stderr)
    success = False
finally:
    end_time = time.perf_counter()
    if success:
        elapsed = end_time - start_time
        print("-" * 40, file=sys.stderr)
        print(f"Solution execution time: {elapsed:.6f} seconds", file=sys.stderr)
        print("-" * 40, file=sys.stderr)
