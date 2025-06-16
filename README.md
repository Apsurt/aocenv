# Advent of Code Environment

Welcome to your personalized development environment for solving [Advent of Code](https://adventofcode.com/) puzzles! This project is designed to streamline your workflow, automate tedious tasks, and let you focus on what's fun: the problem-solving.

It provides a robust command-line interface (CLI) and a Python module to handle everything from fetching puzzle data and submitting answers to archiving your solutions and viewing your progress over the years.

## ✨ Features

* **Interactive Setup**: A one-time `aoc setup` wizard to securely configure your session cookie and preferences.
* **Local Caching**: All puzzle inputs, texts, answers, and submissions are cached locally. This makes the tool incredibly fast and respects the AoC servers by minimizing requests.
* **Full CLI Control**: Manage your entire workflow from the terminal with intuitive commands.
* **Boilerplate Generation**: Kickstart new puzzles instantly with the `aoc start` command.
* **Interactive Stats Viewer**: Get a beautiful, scrollable overview of your progress across all years with `aoc stats`.
* **Solution Management**: Automatically or manually archive your code with `aoc.bind()` and load it back into your workspace with `aoc load`.
* **Safe & Robust**: Built-in safety checks, confirmation prompts for destructive actions.
* **Helpful Logging**: Use the `-v` flag to see what the tool is doing behind the scenes.

## 🚀 Getting Started

### Prerequisites

* Git
* Python 3.8+
* [uv](https://github.com/astral-sh/uv) (or `pip` with `venv`)

### 1. Installation

First, fork the repository. Then clone it and set up the Python environment.

```bash
# Clone your forked repository
git clone https://github.com/Apsurt/aoc-env.git
cd aoc-env

# Create and activate a virtual environment using uv
uv venv
source .venv/bin/activate

# Install the project and its dependencies in editable mode
uv pip install -e ./env_src/

```

### 2. Configuration

This is a mandatory first step. Run the setup wizard to configure your session cookie, which is required to communicate with the AoC website.

```bash
aoc setup
```

The wizard will guide you through finding your cookie in your browser and will ask you about your preferences for auto-binding and auto-clearing.

## 🔧 Workflow

Here is the typical workflow for solving a puzzle from start to finish.

1. Start a New Puzzle

Begin your day by generating a fresh template in your workspace. This populates notepad.py with a useful starting structure.

```bash
aoc start
```

2. Get Oriented

Read the puzzle text and check the input format directly from your terminal.

```bash
# Get the puzzle description (defaults to latest day)
aoc text

# Get the raw puzzle input
aoc input

# Or get data for specific day
aoc text --year 2024 --day 1

# Get the raw puzzle input
aoc input --year 2024 --day 1
```

3. Write Your Solution

Open `notepad.py` in your favorite editor. The file is already set up for you.

-   Uncomment and set `aoc.year`, `aoc.day`, and `aoc.part`.
-   Uncomment `puzzle_input = aoc.get_input()`.
-   Write your code and assign your final calculation to the `answer` variable.

4. Run and Test

Execute your code using the run command. Use the -t flag to time its execution.

```bash
aoc run -t
```

5. Submit and Archive

Once you have an answer, uncomment the `print(aoc.submit(answer))` line in `notepad.py` and run your code again.

```bash
aoc run
```

If your answer is correct, your solution will be automatically bound (if you enabled it during setup). If not, you can add `aoc.bind()` to the end of your script and run it one last time to save it.

6. Start Part 2

To start the next part, you can clear your workspace with aoc clear or load your Part 1 solution back into the notepad to modify it.

```bash
# Load your Part 1 solution for Day 1 of 2024 into notepad.py
aoc load 1 --year 2024 --day 1
```

## 📖 Command Reference

| Command                      | Description                                                                                                    |
| ---------------------------- | -------------------------------------------------------------------------------------------------------------- |
| `aoc setup`                  | Runs the interactive wizard to configure your session cookie and preferences.                                  |
| `aoc sync [--force]`         | Scrapes your progress from AoC, caching all puzzle texts and answers. Can only be run once/day unless forced. |
| `aoc stats`                  | Launches the interactive, scrollable TUI to view your progress stats.                                          |
| `aoc start [-f]`             | Populates `notepad.py` with a boilerplate template. `-f` forces overwrite if not empty.                      |
| `aoc text [opts]`            | Displays the formatted puzzle description.                                                                     |
| `aoc input [opts]`           | Displays the raw puzzle input.                                                                                 |
| `aoc run [-t]`               | Executes the `notepad.py` script. `-t` times the execution.                                                    |
| `aoc load <p> [opts] [-f]`   | Loads a saved solution into `notepad.py`. `<p>` is part 1 or 2. `-f` forces overwrite.                        |
| `aoc list`                   | Lists all your archived solutions from the `solutions/` directory.                                             |
| `aoc clear`                  | Clears all content from `notepad.py`.                                                                          |

**Options for `text`, `input`, and `load`:**
* `--year YYYY`: Specify the puzzle year.
* `--day DD`: Specify the puzzle day.
* If omitted, commands default to the latest puzzle date.

## 🐍 Module Reference (`aoc`)


These functions and variables are available within your `notepad.py` script after `import aoc`.

| Member                | Description                                                                                                 |
| --------------------- | ----------------------------------------------------------------------------------------------------------- |
| `aoc.year = YYYY`     | Sets the year context for all subsequent `aoc` functions.                                                     |
| `aoc.day = DD`        | Sets the day context.                                                                                       |
| `aoc.part = P`        | Sets the part context (1 or 2). **Required** for `submit()` and `bind()`.                                    |
| `aoc.get_input()`     | Returns the puzzle input as a string for the current context.                                               |
| `aoc.submit(answer)`  | Submits your `answer`. Returns a formatted string with the server's response. Caches submissions.             |
| `aoc.bind(overwrite=False)`  | Archives `notepad.py`. Cleans itself from the saved code. `overwrite=True` overwrites an existing file. |
| `aoc.clear()`         | Clears all content from `notepad.py`.                                                                       |

## 📁 Project Structure

```
.
├── .cache/            # Caches all puzzle data and answers
├── .logs/             # Stores detailed log files
├── .venv/             # Your Python virtual environment
├── env_src/           # All the application source code
│   └── aoc/           # The main 'aoc' Python package
├── solutions/         # Your archived solutions are saved here
├── .gitignore         # Standard git ignore file
├── notepad.py         # Your main workspace for solving puzzles
└── README.md          # This file

```

## 💡 Future Ideas

### Automated Testing Framework

The next major feature planned for this environment is a full **Automated Testing Framework**. An `aoc test` command will automatically extract examples from puzzle descriptions and run your code against them, providing instant feedback on your logic.

### Puzzle Solver's Toolkit

Another powerful addition would be to build a library of common utility functions into the `aoc` module (e.g. in an `aoc.utils` submodule). This would provide pre-built, optimized helpers for tasks that appear frequently in Advent of Code, such as:

-   **Grid operations**: Finding neighbors (4-way/8-way), rotating matrices, etc.
-   **Graph algorithms**: Pre-built BFS, DFS, and Dijkstra's algorithm implementations.
-   **Coordinate geometry**: Calculating Manhattan distance, working with 2D/3D points.

This would save you from rewriting the same support code every year, letting you focus purely on the unique aspects of each puzzle.

### Intelligent Input Parsing

To further reduce boilerplate, the `aoc.get_input()` function could be made "smarter". Instead of always returning a raw string, it could attempt to automatically detect the input's format and return a more useful Python data structure. For example:

-   If the input is a list of numbers, it could return a `list[int]`.
-   If the input is a rectangular block of characters, it could return a `list[list[str]]` (a grid).
-   Alternatively, new functions could be added, like `aoc.input_as_lines()` or `aoc.input_as_grid()`, to give the user direct access to pre-parsed data structures.
