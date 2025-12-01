from .constants import MAIN_CONTENTS
from .configuration import get_config
from pathlib import Path


def run_clear():
    config = get_config()

    base_path = Path(config["variables"]["path"])
    main_path = base_path / "main.py"

    year = config.get("variables", "default_year")
    day = config.get("variables", "default_day")
    part = config.get("variables", "default_part")

    with open(main_path, "w") as f:
        f.write(MAIN_CONTENTS.format(year=year, day=day, part=part))
