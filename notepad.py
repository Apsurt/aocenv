import aoc

# --- Context Setting ---
# The puzzle context (year and day) is now set globally via the CLI.
# Use 'aoc context set -y <year> -d <day>' to set it.
# Use 'aoc context show' to see the current setting.


# --- Puzzle Logic ---
#
# Use the InputParser for powerful and flexible input parsing.
# Example: Get a list of integers
# numbers = aoc.get_input_parser().lines().to_ints().get()

# Example: Get a grid of characters
# grid = aoc.get_input_parser().to_grid()

puzzle_input = aoc.get_input()  # Keep simple get_input for basic cases


# Your solution logic here...
def solve(p_input):
	return


with aoc.timed():
	answer = solve(puzzle_input)

# --- Submission ---
# After solving, uncomment the following line and specify the part
# number (1 or 2) to submit your answer.

if answer is not None:
	print(aoc.submit(answer, part=1))

# --- Binding ---
# To save your solution, you can use aoc.bind(part=1)
# aoc.bind(part=1)

# --- Templates ---
# If you want to clean the default template from comment
# and things that you dont want, edit this file and run:
# aoc template save -f default
