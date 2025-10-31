import os
from typing import Optional
from pathlib import Path
from .context import get_context
from .configuration import get_config
from .constants import MAIN_CONTENTS
from .misc import get_solution_filename, get_solution_path

def run_bind(name: Optional[str], force: bool):
    ctx = get_context()
    config = get_config()

    filename = get_solution_filename(ctx, name)

    base_path = Path(config["variables"]["path"])
    main_path = base_path / "main.py"
    bind_path = get_solution_path(base_path, ctx)

    try:
        os.makedirs(bind_path)
    except FileExistsError:
        pass

    bind_path = bind_path / filename

    if os.path.exists(bind_path) and not force:
        print("You already have file binded under that path, use --force if you want to overwrite it")
        return

    with open(main_path, "r") as f:
        contents = f.read()

    with open(bind_path, "w") as f:
        f.write(contents)

    if config["settings"]["clear_on_bind"] == "True":
        with open(main_path, "w") as f:
            f.write(MAIN_CONTENTS)

    if config["settings"]["commit_on_bind"] == "True":
        # TODO v0.2.0
        pass
