from . import _utils

# --- CONTEXT VARIABLES ---
# These can be overridden by the user in their script
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
