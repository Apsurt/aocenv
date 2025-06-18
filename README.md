
# Advent of Code Environment

Welcome to your personalized development environment for solving [Advent of Code](https://adventofcode.com/) puzzles! This project is designed to streamline your workflow, automate tedious tasks, and let you focus on what's fun: the problem-solving.

It provides a robust command-line interface (CLI) and a Python module to handle everything from fetching puzzle data and submitting answers to archiving your solutions and viewing your progress over the years.

## ✨ Features

* **Interactive Setup**: A one-time `aoc setup` wizard to securely configure your session cookie and preferences.
* **Solution Management**: Automatically or manually archive your code with `aoc.bind()` and load it back into your workspace with `aoc load`.
* **Boilerplate Generation**: Kickstart new puzzles instantly with the `aoc start` command.
* **Custom Templates**: Save and load your own boilerplate templates for different kinds of puzzles.
* **Automatic Git Commits**: Optionally auto-commit your solutions with a standardized message upon successful binding.
* **Full CLI Control**: Manage your entire workflow from the terminal with intuitive commands.
* **Stats Viewer**: Get a beautiful, overview of your progress across all years with `aoc stats`.
* **Local Caching**: All puzzle inputs, texts, answers, and submissions are cached locally. This makes the tool incredibly fast and respects the AoC servers by minimizing requests.
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
git clone [https://github.com/Apsurt/aoc-env.git](https://github.com/Apsurt/aoc-env.git)
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

### 1. Set Your Context

Before you begin, tell the environment which puzzle you want to work on. This context is saved and will be used by all subsequent commands.

```bash
# Set the context to December 1st, 2024
aoc context set --year 2024 --day 1

# You can check the current context anytime
aoc context show
```

### 2. Start a New Puzzle

Generate a fresh template in your workspace. This populates `notepad.py` with a useful starting structure.

```bash
aoc start
```

### 3. Get Oriented

Read the puzzle text and check the input format directly from your terminal. These commands automatically use the context you set in step 1.

```bash
# Get the puzzle description for the current context
aoc text

# Get the raw puzzle input for the current context
aoc input
```

### 4. Write Your Solution

Open `notepad.py` in your favorite editor.
- The context is already set, so `aoc.get_input()` will fetch the correct data.
- Write your code and assign your final calculation to the `answer` variable.

### 5. Run and Test

Execute your code using the `run` command. Use the `-t` flag to time its execution.

```bash
aoc run -t
```

### 6. Submit and Archive

Once you have an answer, uncomment the `print(aoc.submit(answer, part=...))` line in `notepad.py`, specify the correct part number (1 or 2), and run your code again.

```bash
aoc run
```

If your answer is correct, your solution will be automatically bound (if you enabled it during setup). If not, you can add `aoc.bind(part=1)` to the end of your script and run it one last time to save it.

### 7. Start Part 2

To start the next part, you can clear your workspace with `aoc clear` or load your Part 1 solution back into the notepad to modify it.

```bash
# Load your Part 1 solution for the current context into notepad.py
aoc load 1
```

## 💾 Custom Templates

You can save the contents of `notepad.py` as a named template to reuse later. This is great for setting up common scenarios, like graph traversal or grid manipulation problems. The environment comes with a standard `default` template, which you can customize to your liking by running `aoc template save default --force`. All templates are stored in the `.templates/` directory.

* **Save a template:** `aoc template save <template_name> [-f]`
* **List all templates:** `aoc template list`
* **Load a template:** `aoc template load <template_name> [-f]`
* **Delete a template:** `aoc template delete <template_name>`

## 🧪 Test Case Management
The `test` command group allows you to manage local test cases for each puzzle. Instead of relying on a fragile scraper, you can manually add the examples from the puzzle description once. This gives you a reliable set of tests to run your code against while you develop. Test cases are stored in `.cache/<year>/<day>/tests.json`.

* **Add a test interactively:** `aoc test add`
* **List saved tests:** `aoc test list`
* **Delete a test:** `aoc test delete <part> <index>`
* **Run tests:** `aoc test run`

## 📖 Command Reference

| Command | Description |
| --- | --- |
| `aoc setup` | Runs the interactive wizard to configure your session cookie and preferences. |
| `aoc context <sub-cmd>` | Manages the persistent puzzle context (`set`, `show`, `clear`). |
| `aoc sync` | Scrapes your star progress from AoC. |
| `aoc stats` | Shows table of all your stars to check your progress stats. |
| `aoc start [NAME] [-f]` | Populates `notepad.py` with a template. Defaults to `default`. |
| `aoc text` | Displays the formatted puzzle description for the current context. |
| `aoc input` | Displays the raw puzzle input for the current context. |
| `aoc run [-t]` | Executes the `notepad.py` script. `-t` times the code inside the `aoc.timed()` block. |
| `aoc perf` | Runs all saved solutions and displays a performance benchmark report. |
| `aoc load <p> [-f]` | Loads a saved solution for the current context into `notepad.py`. `<p>` is part 1 or 2. |
| `aoc list` | Lists all your archived solutions from the `solutions/` directory. |
| `aoc clear` | Clears all content from `notepad.py`. |
| `aoc template <sub-cmd>` | Manages custom templates (`save`, `load`, `list`, `delete`). |
| `aoc test <sub-cmd>` | Manages test cases for puzzles (`add`, `list`, `delete`, `run`). |
| `aoc rm [--all]` | Interactively select and clear cached data, logs, solutions, and configs. `--all` clears everything. |

## 🐍 Module Reference (`aoc`)

These functions are available within your `notepad.py` script after `import aoc`. The `year` and `day` are determined by the context you set via the CLI.

| Member | Description |
| --- | --- |
| `aoc.get_input()` | Returns the puzzle input as a string for the current context. |
| `aoc.submit(answer, part=P)` | Submits your `answer` for Part `P` (1 or 2). Returns a formatted string with the server's response. |
| `aoc.bind(part=P, overwrite=F)` | Archives `notepad.py` for Part `P`. Can trigger auto-commit and auto-clear. `F` is `True` or `False`. |
| `aoc.clear()` | Clears all content from `notepad.py`. |
| `aoc.timed()` | A context manager to accurately time a block of code. Activated by `aoc run -t`. |

## 📁 Project Structure

```
.
├── .cache/            # Caches all puzzle data and answers
├── .context.json      # Stores your current puzzle context (year, day)
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
