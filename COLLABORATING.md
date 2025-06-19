# Collaborating on aoc-env

First off, thank you for considering contributing to this Advent of Code environment! Your help is greatly appreciated.

This document provides guidelines for contributing to the project. Please feel free to propose changes to this document in a pull request.

## How to Contribute

### Getting Started

1.  **Fork the repository** on GitHub.
2.  **Clone your fork** locally:
    ```bash
    git clone https://github.com/YOUR-USERNAME/aoc-env.git
    cd aoc-env
    ```
3.  **Set up your environment**. This project uses `uv` for package and environment management.
    ```bash
    # Create the virtual environment
    uv venv

    # Activate the environment
    source .venv/bin/activate

    # Install the project in editable mode
    uv pip install -e ./env_src/
    ```

### Making Changes

1.  **Create a new branch** for your feature or bugfix.
    ```bash
    git checkout -b your-feature-name
    ```
2.  **Write your code**. Make your changes to the project.
3.  **Update the documentation**. If you are adding a new feature or changing an existing one, please update the `README.md` and `CHANGELOG.md` files accordingly.
4.  **Commit your changes**. Use a descriptive commit message.

### Submitting a Pull Request

1.  **Push your branch** to your fork on GitHub.
    ```bash
    git push origin your-feature-name
    ```
2.  **Open a Pull Request** to the `master` branch of the original repository.
3.  **Write a clear title and description** for your Pull Request, explaining the changes you have made.
4.  **Wait for a review**. Your Pull Request will be reviewed, and you may be asked to make some changes before it is merged.

## Developer Testing

This project uses `pytest` for its internal test suite to ensure the stability and correctness of the `aoc-env` tool itself. These tests are for developers of the tool, not for solving puzzles.

### Setting Up for Testing

Before you can run the tests, you must install the development dependencies:
```bash
uv pip install -e ".[dev]"
```

Thank you again for your contribution!
