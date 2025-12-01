import os
import subprocess
from typing import Optional
from pathlib import Path
from .context import get_context
from .configuration import get_config
from .clear import run_clear
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
        print(
            "You already have file binded under that path, use --force if you want to overwrite it"
        )
        return

    with open(main_path, "r") as f:
        contents = f.read()

    with open(bind_path, "w") as f:
        f.write(contents)

    if config["settings"]["clear_on_bind"] == "True":
        run_clear()

    if config["settings"]["commit_on_bind"] == "True":
        try:
            # Stage the file
            add_result = subprocess.run(
                ["git", "add", str(bind_path)],
                capture_output=True,
                text=True,
                check=False,
            )
            if add_result.returncode != 0:
                print(f"Error staging file: {add_result.stderr}")
                return

            # Construct commit message
            commit_message = f"feat: Solve {ctx.year} Day {ctx.day} Part {ctx.part}"
            if name:
                commit_message += f" ({name})"

            # Commit the file
            commit_result = subprocess.run(
                ["git", "commit", "-m", commit_message],
                capture_output=True,
                text=True,
                check=False,
            )

            if commit_result.returncode == 0:
                print(f'Solution committed to Git: "{commit_message}"')
            else:
                print(f"Error committing file: {commit_result.stderr}")
        except FileNotFoundError:
            print(
                "Git command not found. Please ensure Git is installed and in your PATH."
            )
        except Exception as e:
            print(f"An unexpected error occurred during git commit: {e}")
