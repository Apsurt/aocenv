# src/aoc/timing_context.py
# This file holds the shared state for timing operations.

SUBMIT_TIMINGS = []


def add_submit_time(duration: float):
    """Adds a duration from a submit call to the global list."""
    SUBMIT_TIMINGS.append(duration)


def get_total_submit_time() -> float:
    """Calculates the total time spent in submit calls and clears the list."""
    total = sum(SUBMIT_TIMINGS)
    SUBMIT_TIMINGS.clear()
    return total
