import logging
from pathlib import Path
import re
from . import _utils

# --- CONTEXT VARIABLES ---
year, day = _utils.get_latest_puzzle_date()
part: int | None = None

# --- PUBLIC FUNCTIONS ---

def get_instructions() -> str:
    """
    Gets the puzzle instructions for the current context (year, day).

    Returns:
        A formatted string of the puzzle instructions for the terminal.
    """
    return _utils.get_aoc_data(year, day, data_type="instructions")

def get_input() -> str:
    """
    Gets the puzzle input for the current context (year, day).

    Returns:
        A string containing the raw puzzle input.
    """
    return _utils.get_aoc_data(year, day, data_type="input")

def submit(answer) -> str:
    """
    Submits an answer for the current puzzle context.
    The 'aoc.part' variable must be set.
    """
    logger = logging.getLogger(__name__)
    if part not in [1, 2]:
        err_msg = "aoc.part must be set to 1 or 2 before submitting."
        logger.error(err_msg)
        return err_msg

    response_text = _utils.post_answer(year, day, part, answer)

    if "That's the right answer!" in response_text:
        logger.info("Answer is correct!")
        if _utils.get_bool_config_setting("auto_bind", default=True):
            logger.info("Auto-binding solution...")
            bind()
        return f"✅ {response_text}"
    elif "You don't seem to be solving the right level" in response_text:
            logger.warning(f"Part {part} has already been completed.")
            return f"✅ Part {part} has already been completed. The server did not accept the new submission."
    else:
        logger.warning(f"Answer is incorrect. Response: {response_text}")
        return f"❌ {response_text}"


def bind(overwrite: bool = False):
    """
    Archives the code from notepad.py to the solutions directory.
    The 'aoc.bind()' call is automatically removed from the saved code.
    """
    logger = logging.getLogger(__name__)
    if part not in [1, 2]:
        logger.error("aoc.part must be set to 1 or 2 before binding.")
        return

    source_path = _utils.PROJECT_ROOT / "notepad.py"
    dest_dir = _utils.PROJECT_ROOT / "solutions" / str(year) / f"{day:02d}"
    dest_path = dest_dir / f"part_{part}.py"

    logger.info(f"Binding solution for {year}-{day} Part {part}...")

    if not source_path.exists():
        logger.error("notepad.py not found!")
        return

    if dest_path.exists() and not overwrite:
        logger.warning(f"Solution already exists at {dest_path}. Use bind(overwrite=True) to replace it.")
        return

    try:
        content = source_path.read_text()
        bind_pattern = re.compile(r"^\s*aoc\.bind\s*\(.*\)\s*$", re.MULTILINE)
        cleaned_content = re.sub(bind_pattern, "", content).rstrip()

        dest_dir.mkdir(parents=True, exist_ok=True)
        dest_path.write_text(cleaned_content)
        logger.info(f"Solution successfully saved to {dest_path}")

        if _utils.get_bool_config_setting("auto_clear_on_bind"):
            logger.info("Auto-clearing notepad.py...")
            clear()

    except Exception as e:
        logger.error(f"Failed to bind solution: {e}")

def clear():
    """Clears all content from the notepad.py file."""
    logger = logging.getLogger(__name__)
    notepad_path = _utils.PROJECT_ROOT / "notepad.py"
    if notepad_path.exists():
        notepad_path.write_text("")
        logger.info("notepad.py has been cleared.")
