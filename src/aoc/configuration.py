import os
import click
from .constants import MAIN_CONTENTS

def build_environment(path):
    files = ["main.py", "config.toml"]
    directories = [".aoc", ".aoc/.cache", "solutions", ".aoc/inputs"]

    for dir in directories:
        p = os.path.join(path, dir)
        if not os.path.isdir(p):
            os.mkdir(p)

    for file in files:
        p = os.path.join(path, file)
        with open(p, "w") as f:
            if "main.py" in p:
                f.write(MAIN_CONTENTS)
            else:
                f.write("")

def run_wizard(config):
    config["settings"] = {
        "bind_on_correct": str(click.confirm('Do you want the solution to bind when you submit correct solution?', True)),
        "clear_on_bind": str(click.confirm('Do you want to main.py to be cleared when you bind the soution?')),
        "commit_on_bind": str(click.confirm('Do you want to commit your solution when you bind the solution?')),
    }
    return config
