import aoc

# Set the context for the puzzle you want to solve
# It defaults to the latest, but you can override it
# aoc.year = 2023
# aoc.day = 1

print("--- My AoC Solution Runner ---")
print(f"Fetching data for Year {aoc.year}, Day {aoc.day}")

# Get the puzzle input using the function we built
puzzle_input = aoc.get_input()

# Process the data (example: print the first 5 lines)
lines = puzzle_input.strip().split('\n')
print("\nFirst 5 lines of puzzle input:")
for i, line in enumerate(lines[:5]):
    print(f"  {i+1}: {line}")

print("\nCode execution finished.")
