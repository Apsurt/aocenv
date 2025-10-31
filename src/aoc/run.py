import subprocess
from shutil import which
import os

reg = {
    "uv": ["uv", "run", "main.py"],
    "python": ["python", "main.py"],
    "python3": ["python3", "main.py"]
}

def run_main():

    #TODO add timing of execution

    if not os.path.exists("main.py"):
        RuntimeError("")

    for cmd in ["uv", "python", "python3"]:
        if which(cmd):
            subprocess.run(reg[cmd])
            break
