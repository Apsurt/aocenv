# aocenv

A user-friendly environment management CLI and package for Advent of Code.

`aocenv` is a command-line tool that helps you manage your Advent of Code solutions. It provides a structured environment to save, load, and run your solutions for different days and parts.

## Installation

```bash
pip install aocenv
```

## Configuration

To start using `aocenv`, you need to initialize an environment. This can be done using the `init` command:

```bash
aoc init <path> [session_cookie]
```

- `<path>`: The directory where you want to store your Advent of Code solutions.
- `[session_cookie]`: (Optional) Your Advent of Code session cookie. You can pass this in the configuration wizard. This is required to download puzzle inputs and submit answers.

The `init` command will create a `config.toml` file in the specified path and set up the necessary directory structure.

## Getting your Advent of Code session cookie

To get your Advent of Code session cookie, follow these steps:

1.  Go to [adventofcode.com](https://adventofcode.com).
2.  Log in to your account.
3.  Open your browser's developer tools (usually by pressing F12 or right-clicking and selecting "Inspect").
4.  Go to the "Application" tab (or "Storage" in some browsers).
5.  Expand "Cookies" and select `https://adventofcode.com`.
6.  Find the cookie named `session` and copy its value. This is your session cookie.

## Usage

The main workflow of `aocenv` revolves around the `run`, `bind`, `load`, and `clear` commands.

- `aoc run`: Executes your solution in `main.py`.
- `aoc bind [name]`: Saves the current contents of `main.py` as a solution. You can optionally provide a name for the solution if you want to store more than one solution (for example version with visuallization).
- `aoc load <year> <day> <part> [name]`: Loads a previously saved solution into `main.py`.
- `aoc clear`: Resets the contents of `main.py` to a template.

### Example

1.  **Initialize the environment:**
    ```bash
    aoc init ./aoc-solutions
    ```

2.  **Write your solution** for a specific day and part in the `main.py` file within the `./aoc-solutions` directory.

3.  **Run your solution:**
    ```bash
    aoc run
    ```

4.  **Save your solution:**
    ```bash
    aoc bind
    ```

5.  **Load a different solution:**
    ```bash
    aoc load 2023 1 1
    ```

## Commands

- `aoc init <path> [session_cookie]`: Initializes the environment.
  - `--default`: Use default configuration without running the wizard.
- `aoc run`: Runs the `main.py` file.
- `aoc bind [name]`: Binds the contents of `main.py`.
  - `--force`: Overwrite an existing solution with the same name.
- `aoc load <year> <day> <part> [name]`: Loads a saved solution into `main.py`.
- `aoc clear`: Sets the `main.py` contents to the default.
- `aoc test`: (Coming soon) Runs test cases for your solutions.
