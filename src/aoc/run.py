import subprocess
from shutil import which
import os
import time

reg = {
    "uv": ["uv", "run", "main.py"],
    "python": ["python", "main.py"],
    "python3": ["python3", "main.py"],
}


def run_main(time_it: bool):
    if not os.path.exists("main.py"):
        FileNotFoundError("No main.py found")

    for cmd in ["uv", "python", "python3"]:
        if which(cmd):
            if time_it:
                start_time = time.perf_counter()
                subprocess.run(reg[cmd])
                end_time = time.perf_counter()
                print(f"Execution time: {end_time - start_time:.4f}s")
            else:
                subprocess.run(reg[cmd])
            break
