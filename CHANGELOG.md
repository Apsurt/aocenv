# Changelog

## v0.1.1

### Features
- Implemented `context` command to set default year, day, and part.
- Implemented `auto_bump_on_correct` feature to automatically update context on correct submission.
- Implemented `bind_on_correct` feature to automatically bind solution on correct submission.
- Implemented `commit_on_bind` feature to automatically commit solution after binding.

### Fixes & Improvements
- Updated tests to cover new features.
- Fixed various bugs and improved code quality.

## v0.1.0

### Core Functionality
- Implemented `init`, `run`, `submit`, `clear`, and `bind` commands.
- Added solution loading and execution.

### Input Handling
- Implemented input fetching from Advent of Code website.
- Added input parsing and caching for improved performance.

### Configuration
- Added an interactive configuration wizard (`aoc init`).
- Implemented session cookie handling for authentication.

### Context Management
- Added automatic retrieval of year and day from the environment.
- Implemented context validation.

### Fixes & Improvements
- Numerous bug fixes and stability improvements.
- Improved type hinting and code quality.
