# Gemini Code Assistant Context

## Project Overview

`ai-tokentrace` is a Python library designed for GenAI cost observability. Its primary purpose is to provide developers with a clear and transparent way to track token consumption in applications built with Google's Generative AI. This helps manage operational costs, optimize application performance, and reduce "cost anxiety" for developers.

The library is built as a standalone, distributable package with minimal dependencies, primarily `google-genai` and `pydantic`. It supports Python 3.9 and newer.

## Building and Running

The project uses `uv` for environment and dependency management, and `poethepoet` as a task runner.

*   **Setup:** To set up the development environment, create a virtual environment and install all dependencies:
    ```bash
    uv sync
    ```
    `uv` will automatically create a `.venv` directory if one doesn't exist and manage it for subsequent commands.

*   **Running Tests:** The test suite is run using `pytest` via the `poe` task runner:
    ```bash
    uv run poe test
    ```

*   **Linting and Formatting:** Code quality is maintained with `ruff`, also run via `poe`:
    ```bash
    # Check for linting errors
    uv run poe lint

    # Format the code
    uv run poe format
    ```

## Development Conventions

*   **Dependency Management:** All project metadata and dependencies are managed in `pyproject.toml`.
*   **Code Quality:** The project uses `ruff` for both linting and formatting. Pre-commit hooks are configured in `.pre-commit-config.yaml` to automatically enforce code style and add license headers.
*   **Testing:** The project uses `pytest` for unit testing. Tests are located in the `tests/` directory.
*   **Data Modeling:** Pydantic is used for data modeling and validation to ensure a clear and reliable schema for all exported data.
*   **Commit Messages:** All commit messages must adhere to the Conventional Commits specification.
