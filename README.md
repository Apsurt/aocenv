
# Advent of Code Environment

A personalized development environment for solving [Advent of Code](https://adventofcode.com/) puzzles. This project streamlines your workflow by providing a command-line interface (CLI) to handle everything from fetching puzzle data to submitting your answers.

## 🚀 Getting Started

1.  **Fork the Repository**: Click the **"Fork"** button on the GitHub page to create a copy under your account.
2.  **Clone Your Fork**:
    ```bash
    git clone https://github.com/YOUR-USERNAME/aoc-env.git
    cd aoc-env
    ```
3.  **Set Up Environment & Install**:
    ```bash
    # Create and activate a virtual environment
    python3 -m venv .venv
    source .venv/bin/activate

    # Install the project in editable mode
    pip install -e .
    ```
4.  **Configure Your Session**: Run the one-time setup wizard.
    ```bash
    aoc setup
    ```
5.  **Sync Your Progress**: Fetch your puzzle completion history.
    ```bash
    aoc sync
    ```

You are now ready to start solving puzzles!

## Usage

This environment is designed around a simple, context-driven workflow. You tell the tool which puzzle you're working on, and all subsequent commands will target that puzzle.

### 1. Set the Puzzle Context

First, set the year and day you want to work on. This context is saved automatically.

```bash
# Set the context to December 1st, 2024
aoc context set --year 2024 --day 1

# Check the current context at any time
aoc context show
```

### 2. Start Solving

The `notepad.py` file is your primary workspace. Use the `start` command to populate it with a boilerplate template. This command will also automatically fetch the puzzle input and description for the context you've set.

```bash
# Generate a fresh template in notepad.py
aoc start
```

Now, open `notepad.py` in your editor and start coding.

### 3. Run and Test Your Code

Execute your solution using the `run` command.

```bash
# Run the notepad.py script
aoc run

# Time your code's execution with the -t flag
aoc run -t
```

You can also manage local test cases based on examples from the puzzle description.

```bash
# Interactively add a new test case
aoc test add

# Run your code against all saved test cases for the current puzzle
aoc test run
```

### 4. Submit Your Answer

Once you have a solution, use the `aoc.submit()` function within your `notepad.py` script.

```python
# In notepad.py
from aoc import aoc

answer = 42  # Your calculated answer
print(aoc.submit(answer, part=1))
```

Then, run the script again. If the answer is correct, your solution will be automatically saved.

```bash
aoc run
```

### 5. Manage Solutions

You can load, list, and manage your saved solutions.

```bash
# Load your Part 1 solution back into the notepad
aoc load 1

# List all archived solutions
aoc list
```

## 📖 Command Reference

Here is a list of all available commands. For detailed options on any command, run `aoc <command> --help`.

| Command | Description |
| --- | --- |
| `aoc setup` | Runs the interactive wizard to configure your session cookie and preferences. |
| `aoc context <sub-cmd>` | Manages the puzzle context (`set`, `show`, `clear`). |
| `aoc sync` | Fetches your star progress from the Advent of Code website. |
| `aoc stats` | Displays a table of your progress across all years. |
| `aoc start [NAME] [-f]` | Populates `notepad.py` with a template (defaults to `default`). |
| `aoc text` | Displays the formatted puzzle description for the current context. |
| `aoc input` | Displays the raw puzzle input for the current context. |
| `aoc run [-t]` | Executes `notepad.py`. The `-t` flag times code within the `aoc.timed()` block. |
| `aoc perf` | Runs all saved solutions and displays a performance benchmark report. |
| `aoc plot` | Displays an ASCII bar chart of cached performance data. |
| `aoc load <p> [-f]` | Loads a saved solution for part `<p>` (1 or 2) into `notepad.py`. |
| `aoc list` | Lists all archived solutions from the `solutions/` directory. |
| `aoc clear` | Clears all content from `notepad.py`. |
| `aoc template <sub-cmd>` | Manages custom templates (`save`, `load`, `list`, `delete`). |
| `aoc test <sub-cmd>` | Manages local test cases (`add`, `list`, `delete`, `run`). |
| `aoc rm [--all]` | Interactively clears cached data, logs, solutions, and configs. |

## 🐍 Module Reference (`aoc`)

The `aoc` object provides helper functions to use within your `notepad.py` script.

| Member | Description |
| --- | --- |
| `aoc.get_input()` | Returns the puzzle input as a raw string for the current context. |
| `aoc.get_input_parser()`| Returns a chainable `InputParser` object for advanced parsing. |
| `aoc.submit(answer, part)` | Submits your `answer` for the specified `part` (1 or 2). |
| `aoc.bind(part)` | Archives the current `notepad.py` as the solution for the specified `part`. |
| `aoc.timed()` | A context manager to accurately time a block of code. Activated by `aoc run -t`. |

## 🔧 Project Structure

```
.
├── .cache/            # Caches puzzle data, answers, and logs
├── .venv/             # Your Python virtual environment
├── src/               # Application source code
├── solutions/         # Your archived solutions
├── notepad.py         # Your main workspace for solving puzzles
└── README.md          # This file
```
