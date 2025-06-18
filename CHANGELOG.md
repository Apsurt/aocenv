# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]

### Added
- A new `aoc.timed()` context manager to the `aoc` module for precise timing of solution code.
- A new `aoc perf` command to run all saved solutions, measure their performance, and display a detailed report with statistics.

### Changed
- The `aoc run -t` command now only times the code inside an `aoc.timed()` context block, providing more accurate solution timing by excluding I/O and interpreter overhead.

---

## [1.3.0] - 2025-06-18

This version focuses on major optimizations to the `sync` command and streamlining the developer experience.

### Added
- **Automatic Git Commits**: Added an optional feature, configurable via `aoc setup`, to automatically `git commit` a solution with a standardized message (e.g., `feat(2025-16): Solve Part 1`) after a successful `bind`.
- **Persistent Puzzle Context**: Introduced a new system where the puzzle `year` and `day` are set once and persist across all commands.
- **New `aoc context` Command**: Added a `context` command group to manage the persistent context.
  - `aoc context set --year Y --day D`: Sets and saves the active puzzle context.
  - `aoc context show`: Displays the current context.
  - `aoc context clear`: Clears the saved context, causing the tool to default to the latest puzzle.
- The active context is now stored in a `.context.json` file, which has been added to `.gitignore`.
- **New `aoc rm` Command**: It launches prompt that allows you to select specific categories of data to delete (e.g., cache, logs, solutions). An `--all` flag is provided to clear everything all at once after a confirmation prompt.

### Changed
- `aoc sync` command has been optimized. It no longer downloads puzzle instructions or answers, and only fetches star progress for each year, making it significantly faster.
- Correct answers for solved puzzles are now automatically fetched and cached when you view the puzzle `text` or `input`, not during the `sync` process.
- `aoc stats` is now static and displayed using `tabulate`.

### Fixed
- Corrected `.gitignore` logic to allow `progress.json` to be committed, which is necessary for the auto-commit feature to function correctly.

### Removed
- The `last_sync_timestamp` field from the `progress.json` file.
- The 24-hour rate limit and `--force` flag from the `aoc sync` command.
- The progress bar from the `aoc sync` command, as it's now near-instantaneous.
- Removed the `textual` dependency from the project, simplifying the environment.

---

## [1.2.0] - 2025-06-18

This version introduced a robust, manually-driven testing framework.

### Added
- **Manual Test Management System**: A new `aoc test` command group to give you full control over testing.
  - `aoc test add`: Interactively add a test case (input and expected output) for a puzzle part.
  - `aoc test list`: Lists all saved test cases for a given day.
  - `aoc test delete <part> <index>`: Safely deletes a specific test case with a confirmation prompt.
- **"Test Mode" for `aoc` Module**: The core `aoc` module can now operate in a test mode, managed via environment variables. When active, `aoc.get_input()` provides the example input and `aoc.submit()` performs a local assertion instead of contacting the AoC server.
- **`aoc test run` Command**: The test runner that orchestrates the entire process. It reads `tests.json`, sets the test context, executes `notepad.py` for each case, and provides a summary of pass/fail results.

---

## [1.1.0] - 2025-06-18

This version focused on workflow customization and personalization through templates.

### Added
- **Custom Template Management**: Introduced the `aoc template` command group to allow users to save, load, list, and delete their own custom boilerplate templates.
- **Standardized Default Template**: The default boilerplate is now a physical, user-editable file at `.templates/default.py.template`, making customization transparent.

### Changed
- **Upgraded `aoc start` Command**: `aoc start` is now a powerful alias for `aoc template load`. It loads the `default` template by default but can also accept any custom template name (e.g., `aoc start my_grid_template`).
- The `default` template is now protected from accidental deletion via `aoc template delete default`.

---

## [1.0.0] - 2025-06-18

The initial stable release. This version establishes all core functionalities for a complete, end-to-end puzzle-solving experience.

### Added
- **Initial Project Setup**: A modern Python project using `uv` and a `pyproject.toml` configuration, with all source code organized in an `env_src` directory.
- **Core CLI**: A full suite of commands including `setup`, `sync`, `stats`, `text`, `input`, `run`, `list`, and `clear`.
- **Robust Local Caching**: A `.cache` directory system for all puzzle data, answers, and submissions to minimize server requests and provide offline access.
- **Interactive Stats Viewer**: A fullscreen TUI for the `aoc stats` command, built with `Textual`, to display puzzle progress in a responsive, scrollable grid.
- **Data Sync**: A powerful `aoc sync` command to scrape all personal progress from the AoC website and pre-populate the local cache with puzzle texts and known correct answers.
- **UI & UX Enhancements**:
  - Verbose logging with a `-v` flag.
  - A day-level progress bar for the `sync` command.
  - A `-t` flag for the `run` command to time script execution.
  - Rate-limiting for the `sync` command (once per 24 hours) with a `--force` override.
  - Polished terminal output using colors and Unicode characters.

### Fixed
- Iteratively improved the `sync` scraper to handle multiple different HTML formats found across various years of Advent of Code.
- Resolved timezone bugs in the `sync` rate-limit message.
- Fixed terminal resizing and scrolling bugs in the `stats` TUI.
