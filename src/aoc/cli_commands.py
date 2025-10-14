import os
from .constants import MAIN_CONTENTS

def build_environment(path):
    files = ["main.py", "config.toml"]
    directories = ["", ".cache", "solutions", "inputs"]

    for dir in directories:
        p = os.path.join(path, ".aoc", dir)
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
    return config
