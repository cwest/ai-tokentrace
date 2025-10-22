# Epic Plan: 00-01 Scaffolding and Foundation

**Parent Plan:** [../00-implementation-plan-ai-tokentrace.md](../00-implementation-plan-ai-tokentrace.md)

## Overview
This epic focuses on establishing the foundational structure of the `ai-tokentrace` project. The goal is to create a robust and modern Python project skeleton, complete with all the necessary tooling for development, dependency management, and quality assurance.

## Implementation Tasks

### Phase 1: Project Scaffolding & Foundation (Effort: ~2.5 hours)
1.  **Initialize `pyproject.toml`**
    -   Description: Create and configure the `pyproject.toml` file. Define project metadata, core dependencies (`pydantic`, `google-genai`), and placeholders for optional dependencies.
    -   Files to create: `pyproject.toml`

2.  **Set up Development Environment with `uv`**
    -   Description: Document the process for setting up a virtual environment and installing dependencies using `uv`. Create the initial `src/ai_tokentrace` directory structure.
    -   Files to create: `src/ai_tokentrace/__init__.py`

3.  **Configure Task Runner (`poethepoet`)**
    -   Description: Add `poethepoet` as a development dependency. Configure initial tasks (`lint`, `format`, `test`) in `pyproject.toml` under the `[tool.poe.tasks]` section.
    -   Files to modify: `pyproject.toml`

4.  **Configure `pre-commit` Hooks**
    -   Description: Set up the `.pre-commit-config.yaml` file. Include hooks for code formatting (`ruff format`), linting (`ruff check`), and license headers.
    -   Files to create: `.pre-commit-config.yaml`

5.  **Define Core Data Model**
    -   Description: Create the Pydantic model (`TokenUsageRecord`) that defines the schema for the token usage data, as specified in the PRD.
    -   Files to create: `src/ai_tokentrace/data_model.py`

## Success Criteria
- [ ] `pyproject.toml` is created and fully configured.
- [ ] The `src/ai_tokentrace` directory is created.
- [ ] `poethepoet` is configured with `lint`, `format`, and `test` tasks.
- [ ] `.pre-commit-config.yaml` is created and configured.
- [ ] The `TokenUsageRecord` Pydantic model is defined in `src/ai_tokentrace/data_model.py`.
