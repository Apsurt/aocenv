import subprocess
from shutil import which
import os
import sys
import importlib.resources

def run_main(time_it: bool):
    """
    Runs the user's solution. If timing is requested, it uses the timed_runner.
    """
    if time_it:
        script_path = str(importlib.resources.files('aoc').joinpath('timed_runner.py'))
    else:
        script_path = "main.py"

    if not os.path.exists(script_path):
        # The timed_runner should always exist, so this is for main.py
        raise FileNotFoundError(f"Could not find script to run: {script_path}")

    # Find a python interpreter to run the command
    command_to_run = None
    for cmd_prefix in ["uv", "python", "python3"]:
        if which(cmd_prefix):
            runner = "run" if cmd_prefix == "uv" else ""
            if runner:
                command_to_run = [cmd_prefix, runner, script_path]
            else:
                command_to_run = [cmd_prefix, script_path]
            break

    if command_to_run:
        # Capture the output from the subprocess
        # text=True decodes stdout/stderr as strings
        process = subprocess.run(command_to_run, capture_output=True, text=True, check=False) # check=False to avoid raising CalledProcessError

        # Print the captured stdout and stderr to the parent's stdout/stderr
        # So CliRunner can capture it.
        sys.stdout.write(process.stdout)
        sys.stderr.write(process.stderr)

        if process.returncode != 0:
            sys.exit(process.returncode) # Propagate exit code
    else:
        print(
            "Error: Could not find a Python interpreter ('uv', 'python', 'python3') in your PATH.",
            file=sys.stderr,
        )
